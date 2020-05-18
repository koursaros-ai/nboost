from typing import Dict
from nboost.indexers.base import BaseIndexer
from pysolr import Solr, SolrCoreAdmin

class SolrIndexer(BaseIndexer):
    """Index csvs in Solr"""
    def __init__(self, shards: int = 1, **kwargs):
        super().__init__(**kwargs)

    def format(self, passage: str, cid: str):
        """Format a passage for indexing"""
        body = {
            '_text_': passage
        }

        if cid is not None:
            body['id'] = cid

        return body

    def index(self):
        """send csv to Solr index"""
        self.logger.info('Setting up Solr index...')
        solr = Solr("http://{0}:{1}/solr/travel/".format(self.host, self.port), timeout=10000)
        
        self.logger.info('Indexing %s...' % self.file)
        act = [self.format(passage, cid=cid) for cid, passage in self.csv_generator()]
        solr.add(act)

        solr.optimize()
