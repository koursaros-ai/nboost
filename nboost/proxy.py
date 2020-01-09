"""NBoost Proxy Class"""

from copy import deepcopy
from typing import Tuple
import socket
from nboost.helpers import calculate_overlap, calculate_mrr, dump_json
from nboost.models import resolve_model
from nboost.models.base import BaseModel
from nboost.server import SocketServer
from nboost.models.qa import QAModel
from nboost.session import Session
from nboost import hooks, defaults
from nboost.exceptions import *


class Proxy(SocketServer):
    """The proxy object is the core of NBoost."""
    def __init__(self,
                 uhost: type(defaults.uhost) = defaults.uhost,
                 uport: type(defaults.uport) = defaults.uport,
                 multiplier: type(defaults.multiplier) = defaults.multiplier,
                 delim: type(defaults.delim) = defaults.delim,
                 data_dir: type(defaults.data_dir) = defaults.data_dir,
                 query_path: type(defaults.query_path) = defaults.query_path,
                 search_path: type(defaults.search_path) = defaults.search_path,
                 topk_path: type(defaults.topk_path) = defaults.topk_path,
                 default_topk: type(defaults.default_topk) = defaults.default_topk,
                 cvalues_path: type(defaults.cvalues_path) = defaults.cvalues_path,
                 cids_path: type(defaults.cids_path) = defaults.cids_path,
                 choices_path: type(defaults.choices_path) = defaults.choices_path,
                 rerank: type(defaults.rerank) = defaults.rerank,
                 model: type(defaults.model) = defaults.model,
                 model_dir: type(defaults.model_dir) = defaults.model_dir,
                 qa: type(defaults.qa) = defaults.qa,
                 qa_model: type(defaults.qa_model) = defaults.qa_model,
                 qa_model_dir: type(defaults.qa_model_dir) = defaults.qa_model_dir,
                 qa_threshold: type(defaults.qa_threshold) = defaults.qa_threshold,
                 verbose: type(defaults.verbose) = defaults.verbose, **kwargs):
        kwargs = deepcopy(kwargs)
        kwargs['verbose'] = verbose
        super().__init__(**kwargs)
        self.averages = {}
        self.uhost = uhost
        self.uport = uport
        self.multiplier = multiplier
        self.delim = delim
        self.query_path = query_path
        self.search_path = search_path
        self.topk_path = topk_path
        self.default_topk = default_topk
        self.cvalues_path = cvalues_path
        self.cids_path = cids_path
        self.choices_path = choices_path
        self.rerank = rerank

        self.status = {
            'uhost': self.uhost,
            'uport': self.uport,
            'multiplier': self.multiplier,
            'delim': self.delim,
            'query_path': self.query_path,
            'search_path': self.search_path,
            'topk_path': self.topk_path,
            'default_topk': self.default_topk,
            'cvalues_path': self.cvalues_path,
            'cids_path': self.cids_path,
            'choices_path': self.choices_path
        }

        if self.rerank:
            self.model = resolve_model(
                data_dir=data_dir,
                model_dir=model_dir,
                model_cls=model,
                **kwargs)  # type: BaseModel
            self.status['model'] = type(self.model).__name__
            self.status['model_dir'] = model_dir

        self.qa = qa
        if qa:
            self.qa_model = resolve_model(
                data_dir=data_dir,
                model_dir=qa_model_dir,
                model_cls=qa_model,
                **kwargs)  # type: QAModel
            self.status['model'] = type(self.qa_model).__name__
            self.status['model_dir'] = qa_model_dir

        self.qa_threshold = qa_threshold
        self.description = 'NBoost, for neural boosting.'

    def connect_to_server(self, server_socket):
        """Connect the socket to the server."""
        try:
            server_socket.connect((self.uhost, self.uport))
        except ConnectionRefusedError:
            raise UpstreamConnectionError

    def update_averages(self, **kwargs):
        for key, value in kwargs.items():
            self.averages.setdefault(key, {'count': 0, 'sum': 0})
            item = self.averages[key]
            item['count'] += 1
            item['sum'] += value
            self.status['average_' + key] = item['sum'] / item['count']

    def loop(self, client_socket: socket.socket, address: Tuple[str, str]):
        """Main ioloop for reranking server results to the client"""
        server_socket = self.set_socket()
        session = Session(
            self.delim,
            self.query_path,
            self.topk_path,
            self.default_topk,
            self.cvalues_path,
            self.cids_path,
            self.choices_path
        )

        prefix = 'Request (%s:%s): ' % address

        try:
            self.connect_to_server(server_socket)
            hooks.on_client_request(client_socket, session, self.search_path)
            self.logger.debug(prefix + 'search request.')

            if self.rerank:
                self.update_averages(topk=session.topk)
                session.set_request_path(session.topk_path, session.topk * self.multiplier)

            hooks.on_server_request(server_socket, session)
            hooks.on_server_response(server_socket, session)
            session.response['body']['nboost'] = {}

            if self.rerank:
                if session.rerank_cids:
                    server_mrr = calculate_mrr(session.rerank_cids, session.cids)
                    self.update_averages(server_mrr=server_mrr)

                rerank_time = hooks.on_rerank(self.model, session)
                self.update_averages(rerank_time=rerank_time)

                if session.rerank_cids:
                    model_mrr = calculate_mrr(session.rerank_cids, session.cids)
                    self.update_averages(model_mrr=model_mrr)

            if self.qa:
                if session.cvalues:
                    qa_time = hooks.on_qa(self.qa_model, session, self.qa_threshold)
                    self.update_averages(qa_time=qa_time)

                    first_choice_id = session.cids[0]
                    if first_choice_id in session.qa_cids:
                        qa_start_pos, qa_end_pos = session.qa_cids[first_choice_id]
                        overlap = calculate_overlap(qa_start_pos,qa_end_pos, qa_start_pos, qa_end_pos)
                        self.update_averages(qa_overlap=overlap)

            hooks.on_client_response(session, client_socket)

        except FrontendRequest:
            self.logger.info(prefix + 'frontend request')
            hooks.on_frontend_request(client_socket, session)

        except StatusRequest:
            self.logger.info(prefix + 'status request')
            hooks.on_status_request(client_socket, self.status)

        except UnknownRequest:
            self.logger.info(prefix + 'unknown path "%s"', session.request['url']['path'])
            hooks.on_unhandled_request(client_socket, server_socket, session)

        except MissingQuery:
            self.logger.warning(prefix + 'missing query')
            hooks.on_unhandled_request(client_socket, server_socket, session)

        except UpstreamServerError:
            self.logger.error(prefix + 'server status %s' % session.response['status'])
            hooks.on_client_response(session, client_socket)

        except UpstreamConnectionError as exc:
            self.logger.error(prefix + 'could not connect to %s:%s', self.uhost, self.uport)
            hooks.on_proxy_error(client_socket, exc)

        except InvalidChoices as exc:
            self.logger.warning(prefix + '%s', exc.args)
            hooks.on_unhandled_request(client_socket, server_socket, session)

        except Exception as exc:
            # for misc errors, send back json error msg
            self.logger.error(prefix + str(exc), exc_info=True)
            hooks.on_proxy_error(client_socket, exc)

        finally:
            client_socket.close()
            server_socket.close()

    def run(self):
        """Same as socket server run() but logs"""
        self.logger.info(dump_json(self.status, indent=4).decode())
        super().run()

    def close(self):
        """Close the proxy server and model"""
        self.logger.info('Closing model...')
        self.model.close()
        super().close()
