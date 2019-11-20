from collections import defaultdict
from typing import List, Callable
from tqdm import tqdm
import time


class Benchmarker:
    def __init__(self):
        self.queries = dict()
        self.proxy_avg_mrr = 0
        self.direct_avg_mrr = 0
        self.proxy_avg_ms = 0
        self.direct_avg_ms = 0
        self.proxied_doc_id_producer = None
        self.direct_doc_id_producer = None

        # qids => doc_ids
        self.qrels = defaultdict(set)

    def add_qrel(self, qid: str, doc_id: str):
        """Add query relation"""
        self.qrels[qid].add(doc_id)

    def add_query(self, qid: str, query: str):
        self.queries[qid] = query

    def add_doc_id_producers(self,
                             proxied_doc_id_producer: Callable,
                             direct_doc_id_producer: Callable):
        """Add functions which should return doc ids."""
        self.proxied_doc_id_producer = proxied_doc_id_producer
        self.direct_doc_id_producer = direct_doc_id_producer

    def benchmark(self, rows: int = -1):
        """The benchmark method times the doc_id_producers and
        calculates the mrr."""
        if self.proxied_doc_id_producer is None:
            raise RuntimeError('Must add a doc_id producers to benchmark...')

        # filter queries without relations
        for qid in list(self.queries):
            if qid not in self.qrels:
                self.queries.pop(qid)

        if rows == -1:
            rows = len(self.queries)

        with tqdm(total=rows) as pbar:
            i = 0
            for _ in range(rows):
                qid, query = self.queries.popitem()

                i += 1
                n = i - 1

                _1 = time.perf_counter() * 1000
                proxied_doc_ids = self.proxied_doc_id_producer(query)
                _2 = time.perf_counter() * 1000
                direct_doc_ids = self.direct_doc_id_producer(query)
                _3 = time.perf_counter() * 1000

                ms = _2 - _1
                self.proxy_avg_ms = sum([self.proxy_avg_ms * n, ms]) / i

                ms = _3 - _2
                self.direct_avg_ms = sum([self.direct_avg_ms * n, ms]) / i

                mrr = self.calculate_mrr(qid, proxied_doc_ids)
                self.proxy_avg_mrr = sum([self.proxy_avg_mrr * n, mrr]) / i

                mrr = self.calculate_mrr(qid, direct_doc_ids)
                self.direct_avg_mrr = sum([self.direct_avg_mrr * n, mrr]) / i

                self.set_progress_bar(pbar)

    def set_progress_bar(self, pbar: tqdm):
        proxy_stats = 'PROXY: %.5f MRR %.2f ms/query ' % (
            self.proxy_avg_mrr, self.proxy_avg_ms)
        direct_stats = 'DIRECT: %.5f MRR %.2f ms/query' % (
            self.direct_avg_mrr, self.direct_avg_ms)
        pbar.set_description(proxy_stats + direct_stats)
        pbar.update(1)

    def calculate_mrr(self, qid: str, guessed_doc_ids: List[str]):
        for i, doc_id in enumerate(guessed_doc_ids, 1):
            if doc_id in self.qrels[qid]:
                return 1 / i
        return 0