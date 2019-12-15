from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import streaming_bulk
from elasticsearch import Elasticsearch
from nboost.indexers.base import BaseIndexer


class ESIndexer(BaseIndexer):
    """Index csvs in Elasticsearch"""
    def __init__(self, shards: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.mapping = {'settings': {'index': {'number_of_shards': shards}}}

    def format(self, cid: str, choice: str):
        """Format a choice for indexing"""
        return {
            '_index': self.name, '_id': cid, '_type': '_doc',
            '_source': {self.field_name: choice}
        }

    def index(self):
        """send csv to ES index"""
        self.logger.info('Setting up Elasticsearch index...')
        elastic = Elasticsearch(host=self.host, port=self.port, timeout=10000)
        try:
            self.logger.info('Creating index %s...' % self.name)
            elastic.indices.create(self.name, self.mapping)
        except RequestError:
            self.logger.info('Index already exists, skipping...')

        self.logger.info('Indexing %s...' % self.file)
        act = (self.format(cid, choice) for cid, choice in self.csv_generator())
        list(streaming_bulk(elastic, actions=act))
