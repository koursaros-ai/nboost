from collections import defaultdict
from pathlib import Path
from typing import List
from tqdm import tqdm
from nboost.stats import ClassStatistics
from nboost import DATASET_MAP, PKG_PATH
from nboost.logger import set_logger
from nboost.benchmark import api
from nboost.helpers import (
    csv_generator,
    download_file,
    extract_tar_gz,
    count_lines
)


class Benchmarker:
    """Object used to calculate mean reciprocal rank and latency of search
    ranking. This is necessary to compare the current proxy model performance
    relative to the search-api performance without the proxy.

    The benchmarker assumes that the dataset has three structures:
        queries: query id, query
        documents: ddc id, document
        query relations (qrels): query id, doc id
    """
    stats = ClassStatistics()

    def __init__(self, dataset: str = 'ms_marco', rows: int = 100,
                 connector: str = 'ESConnector', **kwargs):

        self.dataset = dataset
        self.rows = rows
        self.connector = getattr(api, connector)(dataset=dataset, **kwargs)  # type: api.Connector
        self.logger = set_logger(self.__class__.__name__)
        self.queries = dict()
        self.qrels = defaultdict(set)
        self.map = DATASET_MAP[dataset]
        self.cache_path = PKG_PATH.joinpath('.cache/datasets/%s' % dataset)

    def setup(self):
        self.logger.info('Setting up benchmarker...')
        self.connector.setup(self.yield_csv('choices'), self.map['size'])
        self.add_qrels()
        self.add_queries()

    @stats.time_context
    def query_upstream(self, query: str) -> List[int]:
        return self.connector.get_cids(query)

    @stats.time_context
    def query_proxy(self, query: str) -> List[int]:
        return self.connector.get_cids(query, proxy=True)

    @stats.vars_context
    def record_mrr(self, **kwargs):
        """Record the proxy or upstream mrr"""

    def download_and_extract(self):
        file_name = Path(self.map['url']).name
        tar_gz_path = self.cache_path.joinpath(file_name)
        if not self.cache_path.exists():
            self.cache_path.mkdir(parents=True, exist_ok=True)
            self.logger.info('Dowloading to %s' % tar_gz_path)
            download_file(self.map['url'], tar_gz_path)
            self.logger.info('Extracting %s' % tar_gz_path)
            extract_tar_gz(tar_gz_path)
            tar_gz_path.unlink()

    def yield_csv(self, file_type: str):
        file_name, indices, delim = self.map[file_type]
        path = self.cache_path.joinpath(file_name)
        num_lines = count_lines(path)
        with tqdm(total=num_lines, desc=path.name) as pbar:
            for row in csv_generator(path, indices, delim):
                pbar.update()
                yield row

    def add_qrels(self):
        """Add query relations"""
        for qid, doc_id in self.yield_csv('qrels'):
            self.qrels[qid].add(doc_id)

    def add_queries(self):
        """Add query id and text"""
        for qid, query in self.yield_csv('queries'):
            self.queries[qid] = query

    def benchmark(self):
        """The benchmark method times the doc_id_producers and
        calculates the mrr."""
        # filter queries without relations
        for qid in list(self.queries):
            if qid not in self.qrels:
                self.queries.pop(qid)

        maximum = len(self.queries)
        rows = maximum if self.rows == -1 else min(maximum, self.rows)

        with tqdm(total=rows) as pbar:
            for _ in range(rows):
                qid, query = self.queries.popitem()

                proxy_cids = self.query_proxy(query)
                proxy_mrr = self.calculate_mrr(qid, proxy_cids)
                self.record_mrr(proxy_mrr=proxy_mrr)

                upstream_cids = self.query_upstream(query)
                upstream_mrr = self.calculate_mrr(qid, upstream_cids)
                self.record_mrr(upstream_mrr=upstream_mrr)

                self.set_progress_bar(pbar)

    def set_progress_bar(self, pbar: tqdm):
        """Update the progress bar with current statistics"""
        pbar.set_description(
            'PROXY: {proxy_mrr:.5f} MRR {proxy_ms:.2f} ms/query '
            'DIRECT: {direct_mrr:.5f} MRR {direct_ms:.2f} ms/query'.format(
                proxy_mrr=self.stats.record['vars']['proxy_mrr']['avg'],
                direct_mrr=self.stats.record['vars']['upstream_mrr']['avg'],
                proxy_ms=self.stats.record['time']['query_proxy']['avg'],
                direct_ms=self.stats.record['time']['query_upstream']['avg']
            )
        )
        pbar.update()

    def calculate_mrr(self, qid: str, cids: List[int]):
        """Calculate mean reciprocal rank as the first correct result index"""
        for i, cid in enumerate(cids, 1):
            if cid in self.qrels[qid]:
                return 1 / i
        return 0
