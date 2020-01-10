"""NBoost Proxy Class"""

from numbers import Number
from copy import deepcopy
from typing import Tuple
import socket
from nboost.helpers import calculate_overlap, calculate_mrr, dump_json
from nboost.models.base import BaseModel
from nboost.models import resolve_model
from nboost.server import SocketServer
from nboost.models.qa import QAModel
from nboost.session import Session
from nboost import hooks, defaults
from nboost.exceptions import *


class Proxy(SocketServer):
    """The proxy object is the core of NBoost."""
    def __init__(self, search_path: type(defaults.search_path) = defaults.search_path,
                 rerank: type(defaults.rerank) = defaults.rerank,
                 model: type(defaults.model) = defaults.model,
                 model_dir: type(defaults.model_dir) = defaults.model_dir,
                 qa: type(defaults.qa) = defaults.qa,
                 qa_model: type(defaults.qa_model) = defaults.qa_model,
                 qa_model_dir: type(defaults.qa_model_dir) = defaults.qa_model_dir,
                 data_dir: type(defaults.data_dir) = defaults.data_dir, **kwargs):
        super().__init__(**kwargs)
        self.averages = {}
        self.search_path = search_path
        self.rerank = rerank
        self.qa = qa
        self.kwargs = kwargs

        self.status = deepcopy(self.get_session().cli_configs)
        self.status['search_path'] = search_path
        self.status['description'] = 'NBoost, for neural boosting.'

        if self.rerank:
            self.model = resolve_model(
                data_dir=data_dir,
                model_dir=model_dir,
                model_cls=model, **kwargs)  # type: BaseModel
            self.status['model_class'] = type(self.model).__name__
            self.status['model_dir'] = model_dir

        if self.qa:
            self.qa_model = resolve_model(
                data_dir=data_dir,
                model_dir=qa_model_dir,
                model_cls=qa_model,
                **kwargs)  # type: QAModel
            self.status['qa_model_class'] = type(self.qa_model).__name__
            self.status['qa_model_dir'] = qa_model_dir

    def update_averages(self, **stats: Number):
        for key, value in stats.items():
            self.averages.setdefault(key, {'count': 0, 'sum': 0})
            item = self.averages[key]
            item['count'] += 1
            item['sum'] += value
            self.status['average_' + key] = item['sum'] / item['count']

    def get_session(self):
        return Session(**self.kwargs)

    def loop(self, client_socket: socket.socket, address: Tuple[str, str]):
        """Main ioloop for reranking server results to the client"""
        server_socket = self.set_socket()
        session = self.get_session()
        prefix = 'Request (%s:%s): ' % address
        stats = {}

        try:
            hooks.on_client_request(client_socket, session, self.search_path)
            self.logger.debug(prefix + 'search request.')

            if self.rerank:
                stats['topk'] = session.topk
                session.set_request_path(session.topk_path, session.topn)

            hooks.on_server_request(session)

            if self.rerank:
                if session.rerank_cids:
                    stats['server_mrr'] = calculate_mrr(session.rerank_cids, session.cids)

                stats['rerank_time'] = hooks.on_rerank(self.model, session)

                if session.rerank_cids:
                    stats['model_mrr'] = calculate_mrr(session.rerank_cids, session.cids)

            if self.qa:
                if session.cvalues:
                    stats['qa_time'] = hooks.on_qa(self.qa_model, session)

                    if session.cids:
                        first_choice_id = session.cids[0]
                        if first_choice_id in session.qa_cids:
                            qa_start_pos, qa_end_pos = session.qa_cids[first_choice_id]
                            stats['qa_overlap'] = calculate_overlap(qa_start_pos,qa_end_pos, qa_start_pos, qa_end_pos)

            hooks.on_client_response(session, client_socket)

        except FrontendRequest:
            self.logger.info(prefix + 'frontend request')
            hooks.on_frontend_request(client_socket, session)

        except StatusRequest:
            self.logger.info(prefix + 'status request')
            hooks.on_status_request(client_socket, session, self.status)

        except UnknownRequest:
            path = session.get_request_path('url.path')
            self.logger.info(prefix + 'unknown path %s', path)
            hooks.on_unhandled_request(client_socket, server_socket, session)

        except MissingQuery:
            self.logger.warning(prefix + 'missing query')
            hooks.on_unhandled_request(client_socket, server_socket, session)

        except UpstreamServerError as exc:
            self.logger.error(prefix + 'server status %s' % exc)
            hooks.on_client_response(session, client_socket)

        except InvalidChoices as exc:
            self.logger.warning(prefix + '%s', exc.args)
            hooks.on_unhandled_request(client_socket, server_socket, session)

        except Exception as exc:
            # for misc errors, send back json error msg
            self.logger.error(prefix + str(exc), exc_info=True)
            hooks.on_proxy_error(client_socket, exc)

        finally:
            self.update_averages(**stats)
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
