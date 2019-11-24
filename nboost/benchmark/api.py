import elasticsearch
import csv
from nboost.benchmark.benchmarker import Benchmarker
from nboost.base.helpers import *
from nboost import PKG_PATH

REQUEST_TIMEOUT = 10000


class MsMarco(Benchmarker):
    """MSMARCO dataset benchmarker"""
    DEFAULT_URL = ('https://msmarco.blob.core.windows.net'
           '/msmarcoranking/collectionandqueries.tar.gz')
    BASE_DATASET_DIR = PKG_PATH.joinpath('.cache/datasets/ms_marco')

    def __init__(self, args):
        super().__init__(args)
        if not args.url:
            self.url = self.DEFAULT_URL
        else:
            self.url = args.url
        archive_file = self.url.split('/')[-1]
        archive_name = archive_file.split('.')[0]
        self.dataset_dir = self.BASE_DATASET_DIR.joinpath(archive_name)
        self.tar_gz_path = self.dataset_dir.joinpath(archive_file)
        self.qrels_tsv_path = self.dataset_dir.joinpath('qrels.dev.small.tsv')
        self.queries_tsv_path = self.dataset_dir.joinpath('queries.dev.tsv')
        self.collections_tsv_path = self.dataset_dir.joinpath('collection.tsv')
        self.index = 'ms_marco_' + archive_name

        # DOWNLOAD MSMARCO
        if not self.dataset_dir.exists():
            self.dataset_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info('Dowloading MSMARCO to %s' % self.tar_gz_path)
            download_file(self.url, self.tar_gz_path)
            self.logger.info('Extracting MSMARCO')
            extract_tar_gz(self.tar_gz_path, self.dataset_dir)
            self.tar_gz_path.unlink()

        self.proxy_es = Elasticsearch(
            host=self.args.host,
            port=self.args.port,
            timeout=REQUEST_TIMEOUT)
        self.direct_es = Elasticsearch(
            host=self.args.uhost,
            port=self.args.uport,
            timeout=REQUEST_TIMEOUT)

        collection_size = 0
        with open(self.collections_tsv_path) as collection:
            for _ in collection: collection_size += 1

        # INDEX MSMARCO
        try:
            if self.direct_es.count(index=self.index)['count'] < collection_size:
                raise elasticsearch.exceptions.NotFoundError
        except elasticsearch.exceptions.NotFoundError:
            try:
                self.direct_es.indices.create(index=self.index, body={
                    'settings': {
                        'index': {
                            'number_of_shards': args.shards
                        }
                    }
                })
            except: pass
            self.logger.info('Indexing %s' % self.collections_tsv_path)
            es_bulk_index(self.direct_es, self.stream_msmarco_full())

        self.logger.info('Reading %s' % self.qrels_tsv_path)
        with self.qrels_tsv_path.open() as file:
            qrels = csv.reader(file, delimiter='\t')
            for qid, _, doc_id, _ in qrels:
                self.add_qrel(qid, doc_id)

        self.logger.info('Reading %s' % self.queries_tsv_path)
        with self.queries_tsv_path.open() as file:
            queries = csv.reader(file, delimiter='\t')
            for qid, query in queries:
                self.add_query(qid, query)

    def stream_msmarco_full(self):
        self.logger.info('Optimizing streamer...')
        num_lines = sum(1 for _ in self.collections_tsv_path.open())
        with self.collections_tsv_path.open() as fh:
            data = csv.reader(fh, delimiter='\t')
            with tqdm(total=num_lines, desc='INDEXING MSMARCO') as pbar:
                for ident, passage in data:
                    body = dict(_index=self.index,
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
            index=self.index,
            body=body,
            filter_path=['hits.hits._*'])

        doc_ids = [hit['_id'] for hit in res['hits']['hits']]
        return doc_ids


