"""NBoost Proxy Class"""

from typing import List, Tuple
from contextlib import suppress
from pathlib import Path
import socket
import re
from httptools import HttpParserError
from nboost.maps import CONFIG_MAP, MODULE_MAP, CLASS_MAP, URL_MAP
from nboost.protocol import HttpProtocol
from nboost.stats import ClassStatistics
from nboost.server import SocketServer
from nboost.logger import set_logger
from nboost import PKG_PATH
from nboost.helpers import (
    prepare_response,
    prepare_request,
    extract_tar_gz,
    download_file,
    get_jsonpath,
    set_jsonpath,
    import_class,
    dump_json,
    flatten)
from nboost.exceptions import (
    UpstreamConnectionError,
    FrontendRequest,
    UnknownRequest,
    InvalidChoices,
    StatusRequest,
    MissingQuery)


class HttpParserContext:
    """Context that reraises the __context__ of an HttpParserError"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, HttpParserError) and exc_val.__context__:
            raise exc_val.__context__


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
    :param model: uninitialized model class
    :param codex: uninitialized codex class
    """

    stats = ClassStatistics()
    STATIC_PATH = PKG_PATH.joinpath('resources/frontend')

    def __init__(self, data_dir: Path = PKG_PATH.joinpath('.cache'),
                 model_dir: str = 'pt-bert-base-uncased-msmarco',
                 qa_model_dir: str = 'distilbert-base-uncased-distilled-squad',
                 qa_model: str = str(), model: str = str(),
                 qa: bool = False, config: str = 'elasticsearch',
                 verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.qa = qa
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.model_dir = data_dir.joinpath(model_dir).absolute()
        self.model = self.resolve_model(self.model_dir, model, verbose=verbose, **kwargs)
        self.logger = set_logger(self.model.__class__.__name__, verbose=verbose)

        if qa:
            self.qa_model_dir = data_dir.joinpath(qa_model_dir).absolute()
            self.qa_model = self.resolve_model(self.qa_model_dir, qa_model, **kwargs)

        # these are global parameters that are overrided by nboost json key
        self.config = {
            'model': self.model.__class__.__name__, 'model_dir': model_dir,
            'qa_model': self.qa_model.__class__.__name__ if qa else None,
            'qa_model_dir': qa_model_dir if qa else None,
            'data_dir': str(data_dir), **CONFIG_MAP[config], **kwargs
        }

    def resolve_model(self, model_dir: Path, cls: str, **kwargs):
        """Dynamically import class from a module in the CLASS_MAP. This is used
        to manage dependencies within nboost. For example, you don't necessarily
        want to import pytorch models everytime you boot up tensorflow..."""
        if model_dir.exists():
            self.logger.info('Using model cache from %s', model_dir)

            if model_dir.name in CLASS_MAP:
                cls = CLASS_MAP[model_dir.name]
            elif cls not in MODULE_MAP:
                raise ImportError('Class "%s" not in %s.' % CLASS_MAP.keys())

            module = MODULE_MAP[cls]
            model = import_class(module, cls)
            return model(str(model_dir), **kwargs)
        else:
            if model_dir.name in CLASS_MAP:
                cls = CLASS_MAP[model_dir.name]
                module = MODULE_MAP[cls]
                url = URL_MAP[model_dir.name]
                binary_path = self.data_dir.joinpath(Path(url).name)

                if binary_path.exists():
                    self.logger.info('Found model cache in %s', binary_path)
                else:
                    self.logger.info('Downloading "%s" model.', model_dir)
                    download_file(url, binary_path)

                if binary_path.suffixes == ['.tar', '.gz']:
                    self.logger.info('Extracting "%s" from %s', model_dir, binary_path)
                    extract_tar_gz(binary_path, self.data_dir)

                model = import_class(module, cls)
                return model(str(model_dir), **kwargs)

            else:
                if cls in MODULE_MAP:
                    module = MODULE_MAP[cls]
                    model = import_class(module, cls)
                    return model(model_dir.name, **kwargs)
                else:
                    raise ImportError('model_dir %s not found in %s. You must '
                                      'set --model class to continue.'
                                      % (model_dir.name, CLASS_MAP.keys()))

    def on_client_request_url(self, url: dict):
        """Method for screening the url path from the client request"""
        if url['path'].startswith('/nboost/status'):
            raise StatusRequest

        if url['path'].startswith('/nboost'):
            raise FrontendRequest

        if not re.match(self.config['capture_path'], url['path']):
            raise UnknownRequest

    def get_protocol(self) -> HttpProtocol:
        """Return a configured http protocol parser."""
        return HttpProtocol(self.config['bufsize'])

    @stats.time_context
    def frontend_send(self, client_socket, request):
        """Send a the static frontend to the client."""
        response = {}
        protocol = self.get_protocol()
        protocol.set_response_parser()
        protocol.set_response(response)
        response['body'] = self.get_static_file(request['url']['path'])
        client_socket.send(prepare_response(response))

    @stats.time_context
    def status_send(self, client_socket, request):
        """Send a the static frontend to the client."""
        response = {}
        protocol = self.get_protocol()
        protocol.set_response_parser()
        protocol.set_response(response)
        response['body'] = self.status
        response['body'] = dump_json(response['body'], indent=2)
        client_socket.send(prepare_response(response))

    @stats.time_context
    def proxy_send(self, client_socket, server_socket, buffer: bytearray):
        """Send buffered request to server and receive the rest of the original
        client request"""
        protocol = self.get_protocol()
        protocol.set_request_parser()
        protocol.add_data_hook(server_socket.send)
        protocol.feed(buffer)
        protocol.recv(client_socket)

    @stats.time_context
    def proxy_recv(self, client_socket, server_socket):
        """Receive the proxied response and pipe to the client"""
        protocol = self.get_protocol()
        protocol.set_response_parser()
        protocol.add_data_hook(client_socket.send)
        protocol.recv(server_socket)

    @stats.time_context
    def client_recv(self, client_socket, request: dict, buffer: bytearray):
        """Receive client request and pipe to buffer in case of exceptions"""
        protocol = self.get_protocol()
        protocol.set_request_parser()
        protocol.set_request(request)
        protocol.add_data_hook(buffer.extend)
        protocol.add_url_hook(self.on_client_request_url)
        protocol.recv(client_socket)

    @staticmethod
    @stats.time_context
    def server_send(server_socket: socket.socket, request: dict):
        """Send magnified request to the server"""
        request['body'] = dump_json(request['body'])
        request['headers']['content-type'] = 'application/json; charset=UTF-8'
        server_socket.send(prepare_request(request))

    @stats.time_context
    def server_recv(self, server_socket: socket.socket, response: dict):
        """Receive magnified request from the server"""
        protocol = self.get_protocol()
        protocol.set_response_parser()
        protocol.set_response(response)
        protocol.recv(server_socket)

    @staticmethod
    @stats.time_context
    def client_send(request: dict, response: dict, client_socket):
        """Send the ranked results to the client"""
        kwargs = dict(indent=2) if 'pretty' in request['url']['query'] else {}
        response['body'] = dump_json(response['body'], **kwargs)
        client_socket.send(prepare_response(response))

    @stats.time_context
    def error_send(self, client_socket, exc: Exception):
        """Send internal server error to the client."""
        response = {}
        protocol = self.get_protocol()
        protocol.set_response(response)
        response['body'] = dump_json({'error': repr(exc)}, indent=2)
        response['status'] = 500
        client_socket.send(prepare_response(response))

    @stats.time_context
    def model_rank(self, query: str, choices: List[str]) -> List[int]:
        """Rank the query and choices and return the argsorted indices"""
        return self.model.rank(query, choices)

    @stats.vars_context
    def record_topk_and_choices(self, topk: int = None, choices: list = None):
        """Add topk and choices to the running statistical averages"""

    @stats.vars_context
    def record_mrrs(self, upstream_mrr: float = None, model_mrr: float = None):
        """Add the upstream mrr, model mrr, and search boost to the stats"""
        with suppress(ZeroDivisionError):
            var = self.stats.record['vars']
            var['search_boost'] = {
                'avg': var['model_mrr']['avg'] / var['upstream_mrr']['avg']}

    @stats.time_context
    def server_connect(self, server_socket: socket.socket):
        """Connect proxied server socket"""
        uaddress = (self.config['uhost'], self.config['uport'])
        try:
            server_socket.connect(uaddress)
        except ConnectionRefusedError:
            raise UpstreamConnectionError('Connect error for %s:%s' % uaddress)

    @property
    def status(self) -> dict:
        """Return status dictionary in the case of a status request"""
        return {**self.config, **self.stats.record,
                'description': 'NBoost, for search ranking.'}

    def calculate_mrrs(self, true_cids: List[str], cids: List[str],
                       ranks: List[int]):
        """Calculate the mrr of the upstream server and reranked choices from
        the model. This only occurs if the client specified the "nboost"
        parameter in the request url or body."""
        upstream_mrr = self.calculate_mrr(true_cids, cids)
        reranked_cids = [cids[rank] for rank in ranks]
        model_mrr = self.calculate_mrr(true_cids, reranked_cids)
        self.record_mrrs(upstream_mrr=upstream_mrr, model_mrr=model_mrr)

    @staticmethod
    def calculate_mrr(correct: list, guesses: list):
        """Calculate mean reciprocal rank as the first correct result index"""
        for i, guess in enumerate(guesses, 1):
            if guess in correct:
                return 1 / i
        return 0

    def get_static_file(self, path: str) -> bytes:
        """Construct the static path of the frontend asset requested and return
        the raw file."""
        if path == '/nboost':
            asset = 'index.html'
        else:
            asset = path.replace('/nboost/', '', 1)

        static_path = self.STATIC_PATH.joinpath(asset)

        # for security reasons, make sure there is no access to other dirs
        if self.STATIC_PATH in static_path.parents and static_path.exists():
            return static_path.read_bytes()
        else:
            return self.STATIC_PATH.joinpath('404.html').read_bytes()

    @staticmethod
    def get_request_paths(request, configs) -> Tuple[str, int, list]:
        """Get the request jsonpaths noted in the configs"""
        queries = get_jsonpath(request, configs['query_path'])
        topks = get_jsonpath(request, configs['topk_path'])
        true_cids = get_jsonpath(request, configs['true_cids_path'])

        # coerce request variables from their paths
        topk = int(topks[0]) if topks else configs['default_topk']
        query = configs['delim'].join(queries)

        # check for errors
        if not query:
            raise MissingQuery

        return query, topk, true_cids

    @staticmethod
    def get_response_paths(response, configs) -> Tuple[list, list, list]:
        """Get the request jsonpaths noted in the configs"""
        choices = get_jsonpath(response, configs['choices_path'])

        if not isinstance(choices, list):
            raise InvalidChoices('choices were not a list')

        choices = flatten(choices)
        cids = get_jsonpath(choices, '[*].' + configs['cids_path'])
        cvalues = get_jsonpath(choices, '[*].' + configs['cvalues_path'])

        # check for errors
        if not len(choices) == len(cids) == len(cvalues):
            raise InvalidChoices('number of choices, cids, and cvalues differ')

        return choices, cids, cvalues

    def loop(self, client_socket: socket.socket, address: Tuple[str, str]):
        """Main ioloop for reranking server results to the client. Exceptions
        raised in the http parser must be reraised from __context__ because
        they are caught by the MagicStack implementation"""
        buffer = bytearray()
        server_socket = self.set_socket()
        request = {}
        response = {}

        try:
            self.server_connect(server_socket)

            with HttpParserContext():
                # receive and buffer the client request
                self.client_recv(client_socket, request, buffer)
                self.logger.debug('Request (%s:%s): search.', *address)

                # combine runtime configs and preset configs
                configs = {**self.config, **request['body'].get('nboost', {})}

                query, topk, true_cids = self.get_request_paths(request, configs)

                # magnify the size of the request to the server
                new_topk = topk * configs['multiplier']
                set_jsonpath(request, configs['topk_path'], new_topk)

                # send the magnified request to the upstream server
                self.server_send(server_socket, request)
                self.server_recv(server_socket, response)

            if response['status'] < 300:
                choices, cids, cvalues = self.get_response_paths(response, configs)

                self.record_topk_and_choices(topk=topk, choices=choices)

                # use the model to rerank the choices
                ranks = self.model_rank(query, cvalues)[:topk]
                reranked = [choices[rank] for rank in ranks]
                set_jsonpath(response, configs['choices_path'], reranked)

                # if the "nboost" param was sent, calculate MRRs
                if true_cids is not None:
                    self.calculate_mrrs(true_cids, cids, ranks)

                response['body']['nboost'] = {}

                if self.qa and len(cvalues) > 0:
                    answer, offsets, score = self.qa_model.get_answer(query, cvalues[ranks.index(min(ranks))])
                    response['body']['nboost']['qa_model'] = answer
                    response['body']['nboost']['qa_model_offsets'] = offsets
                    response['body']['nboost']['qa_model_score'] = score

            self.client_send(request, response, client_socket)

        except FrontendRequest:
            self.logger.info('Request (%s:%s): frontend request', *address)
            self.frontend_send(client_socket, request)

        except StatusRequest:
            self.logger.info('Request (%s:%s): status request', *address)
            self.status_send(client_socket, request)

        except UnknownRequest:
            self.logger.info('Request (%s:%s): unknown path "%s"',
                             *address, request['url']['path'])
            self.proxy_send(client_socket, server_socket, buffer)
            self.proxy_recv(client_socket, server_socket)

        except MissingQuery:
            self.logger.warning('Request (%s:%s): missing query', *address)
            self.proxy_send(client_socket, server_socket, buffer)
            self.proxy_recv(client_socket, server_socket)

        except InvalidChoices as exc:
            self.logger.warning('Request (%s:%s): %s', *address, *exc.args)
            self.proxy_send(client_socket, server_socket, buffer)
            self.proxy_recv(client_socket, server_socket)

        except Exception as exc:
            # for misc errors, send back json error msg
            self.logger.error('Request (%s:%s): %s.', *address, exc, exc_info=True)
            self.error_send(client_socket, exc)

        finally:
            client_socket.close()
            server_socket.close()

    def run(self):
        """Same as socket server run() but logs"""
        self.logger.info(dump_json(self.config, indent=4).decode())
        super().run()

    def close(self):
        """Close the proxy server and model"""
        self.logger.info('Closing model...')
        self.model.close()
        super().close()
