"""NBoost Proxy Class"""

from typing import Tuple
from pathlib import Path
import socket
import time
from nboost.models import resolve_model
from nboost.models.base import BaseModel
from nboost.server import SocketServer
from nboost.models.qa import QAModel
from nboost.logger import set_logger
from nboost.maps import CONFIG_MAP
from nboost import PKG_PATH, hooks
from nboost.exceptions import *
from nboost.helpers import (
    calculate_overlap,
    calculate_mrr,
    get_jsonpath,
    set_jsonpath,
    dump_json,
    flatten)

RERANK_CIDS = '(body.nboost.rerank.cids) | (url.rerank_cids)'
QA_CIDS = 'body.nboost.qa.cids'


class Proxy(SocketServer):
    """The proxy object is the core of NBoost.
    The following __init__ contains the main executed functions in nboost.

    :param host: virtual host of the server.
    :param port: server port.
    :param uhost: host of the external search api.
    :param uport: search api port.
    :param multiplier: the factor to multiply the search request by. For
        example, in the case of Elasticsearch if the client requests 10
        results and the multiplier is 6, then the model should receive 60
        results to rank and refine down to 10 (better) results.
    :param field: a tag for the field in the search api result that the
        model should rank results by.
    :param model: model class
    """
    def __init__(self, data_dir: Path = PKG_PATH.joinpath('.cache'),
                 model_dir: str = 'pt-bert-base-uncased-msmarco',
                 qa_model_dir: str = 'distilbert-base-uncased-distilled-squad',
                 qa_model: str = str(), model: str = str(), delim: str = '. ',
                 qa: bool = False, config: str = 'elasticsearch',
                 rerank: bool = True, multiplier: int = 5,
                 uhost: str = '0.0.0.0', uport: int = 9200,
                 qa_threshold: float = 0, verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.averages = {}
        self.rerank = rerank
        self.qa = qa
        self.qa_threshold = qa_threshold
        self.multiplier = multiplier
        self.delim = delim
        self.uhost = uhost
        self.uport = uport
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)

        if rerank:
            self.model = resolve_model(
                data_dir=data_dir,
                model_dir=model_dir,
                model_cls=model,
                verbose=verbose, **kwargs)  # type: BaseModel

        if qa:
            self.qa_model = resolve_model(
                data_dir=data_dir,
                model_dir=qa_model_dir,
                model_cls=qa_model,
                verbose=verbose, **kwargs)  # type: QAModel

        _config = {**CONFIG_MAP[config], **kwargs}
        self.query_path = _config['query_path']
        self.choices_path = _config['choices_path']
        self.cids_path = self.choices_path + '.[*].' + _config['cids_path']
        self.cvalues_path = self.choices_path + '.[*].' + _config['cvalues_path']
        self.topk_path = _config['topk_path']
        self.default_topk = _config['default_topk']
        self.search_path = _config['search_path']

        self.status = {
            'configuration': config,
            'model_dir': model_dir if rerank else None,
            'model_class': self.model.__class__.__name__ if rerank else None,
            'qa_model_dir': qa_model_dir if qa else None,
            'qa_model_class': self.qa_model.__class__.__name__ if qa else None,
            'paths': {
                'query': self.query_path,
                'topk': self.topk_path,
                'choices': self.choices_path,
                'cids': self.cids_path,
                'cvalues': self.cvalues_path
            },
            'description': 'NBoost, for search ranking.'
        }

    def connect_to_server(self, server_socket):
        """Connect the socket to the server."""
        try:
            server_socket.connect((self.uhost, self.uport))
        except ConnectionRefusedError:
            raise UpstreamConnectionError

    def get_topk(self, request: dict) -> int:
        topks = get_jsonpath(request, self.topk_path)
        return int(topks[0]) if topks else self.default_topk

    def get_query(self, request: dict) -> str:
        queries = get_jsonpath(request, self.query_path)
        query = self.delim.join(queries)

        # check for errors
        if not query:
            raise MissingQuery

        return query

    def get_cids(self, response: dict) -> list:
        cids = get_jsonpath(response, self.cids_path)
        return flatten(cids)

    def get_rerank_cids(self, request: dict) -> list:
        rerank_cids = get_jsonpath(request, RERANK_CIDS)
        return flatten(rerank_cids)

    def get_qa_cids(self, request: dict) -> dict:
        qa_cids = get_jsonpath(request, QA_CIDS)
        return qa_cids[0] if qa_cids else None

    def get_cvalues(self, response: dict) -> list:
        return get_jsonpath(response, self.cvalues_path)

    def get_choices(self, response: dict) -> list:
        choices = get_jsonpath(response, self.choices_path)

        if not isinstance(choices, list):
            raise InvalidChoices('choices were not a list')

        return flatten(choices)

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
        buffer = bytearray()
        request = {}
        response = {}
        prefix = 'Request (%s:%s): ' % address

        try:
            self.connect_to_server(server_socket)

            hooks.on_client_request(client_socket, request, buffer, self.search_path)
            self.logger.debug(prefix + 'search request.')

            topk = self.get_topk(request)
            query = self.get_query(request)

            if self.rerank:
                self.update_averages(topk=topk)
                set_jsonpath(request, self.topk_path, topk * self.multiplier)

            hooks.on_server_request(server_socket, request)
            hooks.on_server_response(server_socket, response)

            if self.rerank:
                choices = self.get_choices(response)
                cids = self.get_cids(response)
                cvalues = self.get_cvalues(response)
                rerank_cids = self.get_rerank_cids(request)

                if rerank_cids:
                    server_mrr = calculate_mrr(rerank_cids, cids)
                    self.update_averages(server_mrr=server_mrr)

                start_time = time.perf_counter()
                ranks = self.model.rank(query, cvalues)[:topk]
                total_time = time.perf_counter() - start_time
                self.update_averages(rerank_time=total_time)
                reranked_choices = [choices[rank] for rank in ranks]
                set_jsonpath(response, self.choices_path, reranked_choices)
                cids = self.get_cids(response)

                if rerank_cids:
                    model_mrr = calculate_mrr(rerank_cids, cids)
                    self.update_averages(model_mrr=model_mrr)

            if self.qa:
                cids = self.get_cids(response)
                cvalues = self.get_cvalues(response)
                qa_cids = self.get_qa_cids(request)

                if cids and cvalues:
                    start_time = time.perf_counter()
                    answer, start_pos, end_pos, score = self.qa_model.get_answer(query, cvalues[0])
                    total_time = time.perf_counter() - start_time
                    self.update_averages(qa_time=total_time)

                    if score > self.qa_threshold:
                        response['body']['nboost']['qa'] = {
                            'answer': answer,
                            'start_pos': start_pos,
                            'end_pos': end_pos,
                            'score': score
                        }
                        if qa_cids and cids[0] in qa_cids.keys():
                            qa_start_pos, qa_end_pos = qa_cids[cids[0]]
                            overlap = calculate_overlap(qa_start_pos,qa_end_pos, start_pos, end_pos)
                            self.update_averages(qa_overlap=overlap)

            hooks.on_client_response(request, response, client_socket)

        except FrontendRequest:
            self.logger.info(prefix + 'frontend request')
            hooks.on_frontend_request(client_socket, request)

        except StatusRequest:
            self.logger.info(prefix + 'status request')
            hooks.on_status_request(client_socket, self.status)

        except UnknownRequest:
            self.logger.info(prefix + 'unknown path "%s"', request['url']['path'])
            hooks.on_unhandled_request(client_socket, server_socket, buffer)

        except MissingQuery:
            self.logger.warning(prefix + 'missing query')
            hooks.on_unhandled_request(client_socket, server_socket, buffer)

        except UpstreamServerError:
            self.logger.error(prefix + 'server status %s' % response['status'])
            hooks.on_client_response(request, response, client_socket)

        except UpstreamConnectionError as exc:
            self.logger.error(prefix + 'could not connect to %s:%s', self.uhost, self.uport)
            hooks.on_proxy_error(client_socket, exc)

        except InvalidChoices as exc:
            self.logger.warning(prefix + '%s', exc.args)
            hooks.on_unhandled_request(client_socket, server_socket, buffer)

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
