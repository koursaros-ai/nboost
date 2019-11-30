from abc import abstractmethod
from typing import List, Generator
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import streaming_bulk
from elasticsearch import Elasticsearch
from nboost.logger import set_logger


class Connector:
    """The connector is the object that the benchmarker uses to return cids
    from a search api."""

    def __init__(self, topk: int = 10, dataset: str = 'ms_marco',
                 host: str = '0.0.0.0', port: int = 8000,
                 uhost: str = '0.0.0.0', uport: int = 9200,
                 field: str = 'passage', **kwargs):
        self.topk = topk
        self.host = host
        self.port = port
        self.uhost = uhost
        self.uport = uport
        self.field = field
        self.dataset = dataset
        self.logger = set_logger(self.__class__.__name__)

    @abstractmethod
    def setup(self, choice_generator: Generator, total: int):
        """Setup the search api (e.g. index, settings, etc).

        :param choice_generator: generates choice id, choice tuples
        :param total: total number of choices
        """

    @abstractmethod
    def get_cids(self, query: str, proxy=False) -> List[int]:
        """return the predicted choice ids given a query."""


class ESConnector(Connector):
    def __init__(self, shards: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.mapping = {'settings': {'index': {'number_of_shards': shards}}}
        self.proxy_elastic = self.set_elastic(self.host, self.port)
        self.upstream_elastic = self.set_elastic(self.uhost, self.uport)

    @staticmethod
    def set_elastic(host: str, port: int) -> Elasticsearch:
        """Construct elastic api"""
        return Elasticsearch(host=host, port=port, timeout=10000)

    def format(self, cid: int, choice: str):
        """Format a choice for indexing"""
        return {
            '_index': self.dataset, '_id': cid,
            '_source': {self.field: choice}
        }

    def setup(self, choice_gen: Generator, total: int):
        self.logger.info('Setting up Elasticsearch index...')
        try:
            if self.upstream_elastic.count(index=self.dataset)['count'] < total:
                raise NotFoundError
            else:
                self.logger.info('Index exists!')
        except NotFoundError:
            # with suppress(Exception):
            self.logger.info('Creating index %s...' % self.dataset)
            self.upstream_elastic.indices.create(self.dataset, self.mapping)
            self.logger.info('Indexing %s...' % self.dataset)

            act = (self.format(cid, choice) for cid, choice in choice_gen)
            list(streaming_bulk(self.upstream_elastic, actions=act))

    def get_cids(self, query: str, proxy=False):
        elastic = self.proxy_elastic if proxy else self.upstream_elastic

        return [
            hit['_id'] for hit in elastic.search(
                index=self.dataset,
                body={'size': self.topk, 'query': {"match": {self.field: {"query": query}}}},
                filter_path=['hits.hits._*']
            )['hits']['hits']
        ]

