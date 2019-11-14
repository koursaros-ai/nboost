from nboost.benchmark.benchmarker import Benchmarker
from nboost.base.helpers import *
from nboost import PKG_PATH
import csv

REQUEST_TIMEOUT = 10000


def msmarco(args) -> Benchmarker:
    index = 'ms_marco'
    url = 'https://msmarco.blob.core.windows.net/msmarcoranking/collectionandqueries.tar.gz'
    dataset_dir = PKG_PATH.joinpath('.cache/datasets/ms_marco')
    tar_gz_path = dataset_dir.joinpath('collectionandqueries.tar.gz')
    qrels_tsv_path = dataset_dir.joinpath('qrels.dev.small.tsv')
    queries_tsv_path = dataset_dir.joinpath('queries.dev.tsv')
    collections_tsv_path = dataset_dir.joinpath('collection.tsv')

    # DOWNLOAD MSMARCO
    if not dataset_dir.exists():
        dataset_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_dir.exists():
        print('Dowloading MSMARCO to %s' % tar_gz_path)
        download_file(url, tar_gz_path)
        print('Extracting MSMARCO')
        extract_tar_gz(tar_gz_path, dataset_dir)
        tar_gz_path.unlink()

    # INDEX MSMARCO
    proxy_es = Elasticsearch(host=args.host, port=args.port, timeout=REQUEST_TIMEOUT)
    direct_es = Elasticsearch(host=args.ext_host, port=args.ext_port, timeout=REQUEST_TIMEOUT)

    def stream_msmarco_full():
        print('Optimizing streamer...')
        num_lines = sum(1 for line in collections_tsv_path.open())
        with collections_tsv_path.open() as fh:
            data = csv.reader(fh, delimiter='\t')
            with tqdm(total=num_lines, desc='INDEXING MSMARCO') as pbar:
                for ident, passage in data:
                    body = dict(_index=index, _id=ident, _source={'passage': passage})
                    yield body
                    pbar.update(1)

    try:
        if proxy_es.count(index=index)['count'] < 8 * 10 ** 6:
            raise elasticsearch.exceptions.NotFoundError
    except elasticsearch.exceptions.NotFoundError:
        es_bulk_index(proxy_es, stream_msmarco_full())

    # BENCHMARK MSMARCO
    benchmarker = Benchmarker()

    def es_doc_id_producer(es: Elasticsearch):
        def querier(query: str):
            body = dict(size=args.topk, query={"match": {"passage": {"query": query}}})
            res = es.search(index=index, body=body, filter_path=['hits.hits._*'])
            doc_ids = [hit['_id'] for hit in res['hits']['hits']]
            return doc_ids
        return querier

    benchmarker.add_doc_id_producers(
        es_doc_id_producer(proxy_es),
        es_doc_id_producer(direct_es)
    )

    with qrels_tsv_path.open() as file:
        qrels = csv.reader(file, delimiter='\t')
        for qid, _, doc_id, _ in qrels:
            benchmarker.add_qrel(qid, doc_id)

    with queries_tsv_path.open() as file:
        queries = csv.reader(file, delimiter='\t')
        for qid, query in queries:
            benchmarker.add_query(qid, query)

    return benchmarker


