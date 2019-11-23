from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from elasticsearch.exceptions import TransportError
from nboost.tutorial import RESOURCES
from nboost.base.logger import set_logger


class Tutorial:
    """Base Tutorial Object"""
    def __init__(self, args):
        self.args = args
        self.logger = set_logger(self.__class__.__name__)

    def setup(self):
        """The tutorial cli runs this before running run()"""

    def run(self):
        """Main tutorial functionality"""

    def cleanup(self):
        """Cleanup the tutorial class"""


class Travel(Tutorial):
    """Elasticsearch support for a travel/hotels subset of MSMARCO"""
    INDEX = 'travel'
    FIELD = 'passage'
    FILE = RESOURCES.joinpath('travel.txt')
    MAPPING = {"properties": {FIELD: {"type": "text"}}}
    SETTINGS = {"index": {"number_of_shards": 5, "number_of_replicas": 0}}
    DICT = dict(mappings=MAPPING, settings=SETTINGS)

    def setup(self):
        """Creates a "travel" elasticsearch index from travel.txt"""
        address = (self.args.host, self.args.port)
        elastic = Elasticsearch(host=address[0], port=address[1])

        # attempt to reset index
        try:
            response = elastic.indices.delete(self.INDEX)
            self.logger.info(response)
        except TransportError:
            pass

        self.logger.info('Creating travel index on %s:%s' % address)
        response = elastic.indices.create(index=self.INDEX, body=self.DICT)
        self.logger.info(response)
        self.logger.info('Indexing %s' % self.FILE)
        txt = self.FILE.open()
        gen = (dict(_index=self.INDEX, _source={self.FIELD: x}) for x in txt)

        # empty iterator
        list(streaming_bulk(elastic, actions=gen))
        txt.close()
