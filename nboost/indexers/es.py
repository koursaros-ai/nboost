from typing import Dict
from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import streaming_bulk
from elasticsearch import Elasticsearch
from nboost.indexers.base import BaseIndexer


class ESIndexer(BaseIndexer):
    """Index csvs in Elasticsearch"""
    def __init__(self, shards: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.mapping = {'settings': {'index': {'number_of_shards': shards}}}

    def format(self, choices: Dict[str, str], cid: str = None):
        """Format a choice for indexing"""
        body = {
            '_index': self.index_name,
            '_type': '_doc',
            '_source': choices
        }

        if cid is not None:
            body['_id'] = cid

        return body

    def index(self):
        """send csv to ES index"""
        self.logger.info('Setting up Elasticsearch index...')
        elastic = Elasticsearch(host=self.host, port=self.port, timeout=10000)
        try:
            self.logger.info('Creating index %s...' % self.index_name)
            elastic.indices.create(self.index_name, self.mapping)
        except RequestError:
            self.logger.info('Index already exists, skipping...')

        self.logger.info('Indexing %s...' % self.file)
        act = (self.format(choices, cid=cid) for cid, choices in self.csv_generator())
        list(streaming_bulk(elastic, actions=act))
