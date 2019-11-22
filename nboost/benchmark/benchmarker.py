from collections import defaultdict
from typing import List
from tqdm import tqdm
from ..base.helpers import TimeContext
from ..base.logger import set_logger
from argparse import Namespace


class Benchmarker:
    """Object used to calculate mean reciprocal rank and latency of search
    ranking. This is necessary to compare the current proxy model performance
    relative to the search-api performance without the proxy.

    The benchmarker assumes that the dataset has three structures:
        queries: query id, query
        documents: ddc id, document
        query relations (qrels): query id, doc id
    """
    time_context = TimeContext()

    def __init__(self, args: Namespace):
        self.logger = set_logger(self.__class__.__name__)
        self.args = args
        self.queries = dict()
        self.proxy_avg_mrr = 0
        self.direct_avg_mrr = 0
        self.qrels = defaultdict(set)

    def add_qrel(self, qid: str, doc_id: str):
        """Add query relation"""
        self.qrels[qid].add(doc_id)

    def add_query(self, qid: str, query: str):
        """Add query id and text"""
        self.queries[qid] = query

    def proxied_doc_id_producer(self, query: str):
        """Returns ranked doc ids from the proxy"""
        raise NotImplementedError

    def direct_doc_id_producer(self, query: str):
        """Returns ranked doc ids from the server (without the proxy ranks)"""
        raise NotImplementedError

    def benchmark(self):
        """The benchmark method times the doc_id_producers and
        calculates the mrr."""
        # filter queries without relations
        for qid in list(self.queries):
            if qid not in self.qrels:
                self.queries.pop(qid)

        rows = len(self.queries) if self.args.rows == -1 else self.args.rows

        with tqdm(total=rows) as pbar:
            for i in range(1, rows + 1):
                qid, query = self.queries.popitem()
                context = (qid, query, i)
                self.proxy_avg_mrr = self.query_proxy(*context)
                self.direct_avg_mrr = self.query_direct(*context)
                self.set_progress_bar(pbar)

    @time_context
    def query_proxy(self, *context) -> float:
        return self.get_new_mrr(self.proxied_doc_id_producer,
                                self.proxy_avg_mrr, *context)

    @time_context
    def query_direct(self, *context) -> float:
        return self.get_new_mrr(self.direct_doc_id_producer,
                                self.direct_avg_mrr, *context)

    def get_new_mrr(self, doc_id_producer, old_avg_mrr, qid, query, i):
        guessed_doc_ids = doc_id_producer(query)
        mrr = self.calculate_mrr(qid, guessed_doc_ids)
        return self.running_avg(old_avg_mrr, mrr, i)

    @staticmethod
    def running_avg(old_avg: float, new_entry: float, iteration: int):
        """Running average of floats"""
        return sum([old_avg * (iteration - 1), new_entry]) / iteration

    def set_progress_bar(self, pbar: tqdm):
        """Update the progress bar with current statistics"""
        pam = self.proxy_avg_mrr
        dam = self.direct_avg_mrr
        rqp = self.time_context.record['query_proxy']['avg']
        rqd = self.time_context.record['query_direct']['avg']
        pbar.set_description('PROXY: %.5f MRR %.2f ms/query ' % (pam, rqp) + \
                             'DIRECT: %.5f MRR %.2f ms/query' % (dam, rqd))
        pbar.update()

    def calculate_mrr(self, qid: str, guessed_doc_ids: List[str]):
        """Calculate mean reciprocal rank as the first correct result index"""
        for i, doc_id in enumerate(guessed_doc_ids, 1):
            if doc_id in self.qrels[qid]:
                return 1 / i
        return 0
