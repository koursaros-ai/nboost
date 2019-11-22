import elasticsearch
import csv
from nboost.benchmark.benchmarker import Benchmarker
from nboost.base.helpers import *
from nboost import PKG_PATH

REQUEST_TIMEOUT = 10000


class MsMarco(Benchmarker):
    """MSMARCO dataset benchmarker"""
    INDEX = 'ms_marco'
    URL = ('https://msmarco.blob.core.windows.net'
           '/msmarcoranking/collectionandqueries.tar.gz')
    DATASET_DIR = PKG_PATH.joinpath('.cache/datasets/ms_marco')
    TAR_GZ_PATH = DATASET_DIR.joinpath('collectionandqueries.tar.gz')
    QRELS_TSV_PATH = DATASET_DIR.joinpath('qrels.dev.small.tsv')
    QUERIES_TSV_PATH = DATASET_DIR.joinpath('queries.dev.tsv')
    COLLECTIONS_TSV_PATH = DATASET_DIR.joinpath('collection.tsv')

    def __init__(self, args):
        super().__init__(args)

        # DOWNLOAD MSMARCO
        if not self.DATASET_DIR.exists():
            self.DATASET_DIR.mkdir(parents=True, exist_ok=True)
            self.logger.info('Dowloading MSMARCO to %s' % self.TAR_GZ_PATH)
            download_file(self.URL, self.TAR_GZ_PATH)
            self.logger.info('Extracting MSMARCO')
            extract_tar_gz(self.TAR_GZ_PATH, self.DATASET_DIR)
            self.TAR_GZ_PATH.unlink()

        self.proxy_es = Elasticsearch(
            host=self.args.host,
            port=self.args.port,
            timeout=REQUEST_TIMEOUT)
        self.direct_es = Elasticsearch(
            host=self.args.uhost,
            port=self.args.uport,
            timeout=REQUEST_TIMEOUT)

        # INDEX MSMARCO
        try:
            if self.direct_es.count(index=self.INDEX)['count'] < 8 * 10 ** 6:
                raise elasticsearch.exceptions.NotFoundError
        except elasticsearch.exceptions.NotFoundError:
            self.logger.info('Indexing %s' % self.COLLECTIONS_TSV_PATH)
            es_bulk_index(self.direct_es, self.stream_msmarco_full())

        self.logger.info('Reading %s' % self.QRELS_TSV_PATH)
        with self.QRELS_TSV_PATH.open() as file:
            qrels = csv.reader(file, delimiter='\t')
            for qid, _, doc_id, _ in qrels:
                self.add_qrel(qid, doc_id)

        self.logger.info('Reading %s' % self.QUERIES_TSV_PATH)
        with self.QUERIES_TSV_PATH.open() as file:
            queries = csv.reader(file, delimiter='\t')
            for qid, query in queries:
                self.add_query(qid, query)

    def stream_msmarco_full(self):
        self.logger.info('Optimizing streamer...')
        num_lines = sum(1 for _ in self.COLLECTIONS_TSV_PATH.open())
        with self.COLLECTIONS_TSV_PATH.open() as fh:
            data = csv.reader(fh, delimiter='\t')
            with tqdm(total=num_lines, desc='INDEXING MSMARCO') as pbar:
                for ident, passage in data:
                    body = dict(_index=self.INDEX,
                                _id=ident, _source={'passage': passage})
                    yield body
                    pbar.update()

    def proxied_doc_id_producer(self, query: str):
        return self.es_doc_id_producer(self.proxy_es, query)

    def direct_doc_id_producer(self, query: str):
        return self.es_doc_id_producer(self.direct_es, query)

    def es_doc_id_producer(self, es: Elasticsearch, query: str):
        body = dict(
            size=self.args.topk,
            query={"match": {"passage": {"query": query}}})

        res = es.search(
            index=self.INDEX,
            body=body,
            filter_path=['hits.hits._*'])

        doc_ids = [hit['_id'] for hit in res['hits']['hits']]
        return doc_ids


