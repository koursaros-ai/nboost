"""NBoost command line interface"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter as AdHf
import termcolor
from nboost.__version__ import __doc__
from nboost import defaults


TAG = termcolor.colored('NBoost (v%s)' % __doc__, 'cyan', attrs=['underline'])
DESCRIPTION = ('%s: is a scalable, search-api-boosting platform for '
               'developing and deploying SOTA models to improve the '
               'relevance of search results..' % TAG)
QA_MODEL = 'adds the qa plugin which treats the query as a question and marks the answer offset'
FILTER_RESULTS = 'whether to filter out results based on classification model'
DELIM = 'the deliminator to concatenate multiple queries into a single query'
CIDS_PATH = 'the jsonpath to find the ids of the choices (for benchmarking)'
QUERY_PREP = 'preprocessing filter applied to the query string after request and before reranking'
CVALUES_PATH = 'the jsonpath to find the string values of the choices'
CHOICES_PATH = 'the jsonpath to find the array of choices to reorder'
TOPK_PATH = 'the jsonpath to find the number of requested results'
DEFAULT_TOPK = 'the default number of results that the api returns'
TRUE_CIDS_PATH = 'the path of the true choice ids in the request'
SEARCH_PATH = 'the url path to tag for reranking via nboost'
QUERY_PATH = 'the jsonpath in the request to find the query'
QA_MODEL_DIR = 'name or directory of the finetuned qa model'
CONFIG = 'which search api nboost should be configured for'
BATCH_SIZE = 'batch size for running through rerank model'
MODEL_DIR = 'name or directory of the finetuned model'
WORKERS = 'number of threads serving the proxy'
TOPN = 'the number of results to rerank (filtered down to topk)'
QA = 'whether or not to output qa responses'
MAX_SEQ_LEN = 'max combined token length'
VERBOSE = 'turn on detailed logging'
BUFSIZE = 'size of the http buffer'
LR = 'learning rate of the model'
DATA_DIR = 'dir for model binary'
UHOST = 'host of the server'
UPORT = 'port of the server'
PROTOCOL = 'protocol class'
HOST = 'host of the proxy'
PORT = 'port of the proxy'
MODEL = 'model class'
RERANK = 'whether to rerank the query results using the model'
USSL = 'use ssl for the upstream connection'
DEBUG = 'return the session parameters and parsed objects for that session'


def set_parser() -> ArgumentParser:
    """Add default nboost cli arguments to a given parser"""
    parser = ArgumentParser(prog='nboost', description=DESCRIPTION,
                            formatter_class=lambda prog: AdHf(prog, max_help_position=100, width=100))
    parser.add_argument('--debug', type=type(defaults.debug), default=defaults.debug, help=DEBUG)
    parser.add_argument('--rerank', type=type(defaults.rerank), default=defaults.rerank, help=RERANK)
    parser.add_argument('--search_path', type=type(defaults.search_path), default=defaults.search_path, help=SEARCH_PATH)
    parser.add_argument('--query_path', type=type(defaults.query_path), default=defaults.query_path, help=QUERY_PATH)
    parser.add_argument('--topk_path', type=type(defaults.topk_path), default=defaults.topk_path, help=TOPK_PATH)
    parser.add_argument('--default_topk', type=type(defaults.default_topk), default=defaults.default_topk, help=DEFAULT_TOPK)
    parser.add_argument('--cvalues_path', type=type(defaults.cvalues_path), default=defaults.cvalues_path, help=CVALUES_PATH)
    parser.add_argument('--cids_path', type=type(defaults.cids_path), default=defaults.cids_path, help=CIDS_PATH)
    parser.add_argument('--choices_path', type=type(defaults.choices_path), default=defaults.choices_path, help=CHOICES_PATH)
    parser.add_argument('--query_prep', type=type(defaults.query_prep), default=defaults.query_prep, help=QUERY_PREP)
    parser.add_argument('--verbose', type=type(defaults.verbose), default=defaults.verbose, help=VERBOSE)
    parser.add_argument('--host', type=type(defaults.host), default=defaults.host, help=HOST)
    parser.add_argument('--port', type=type(defaults.port), default=defaults.port, help=PORT)
    parser.add_argument('--uhost', type=type(defaults.uhost), default=defaults.uhost, help=UHOST)
    parser.add_argument('--uport', type=type(defaults.uport), default=defaults.uport, help=UPORT)
    parser.add_argument('--ussl', type=type(defaults.ussl), default=defaults.ussl, help=USSL)
    parser.add_argument('--delim', type=type(defaults.delim), default=defaults.delim, help=DELIM)
    parser.add_argument('--lr', type=type(defaults.lr), default=defaults.lr, help=LR)
    parser.add_argument('--max_seq_len', type=type(defaults.max_seq_len), default=defaults.max_seq_len, help=MAX_SEQ_LEN)
    parser.add_argument('--bufsize', type=type(defaults.bufsize), default=defaults.bufsize, help=BUFSIZE)
    parser.add_argument('--batch_size', type=type(defaults.batch_size), default=defaults.batch_size, help=BATCH_SIZE)
    parser.add_argument('--topn', type=type(defaults.topn), default=defaults.topn, help=TOPN)
    parser.add_argument('--workers', type=type(defaults.workers), default=defaults.workers, help=WORKERS)
    parser.add_argument('--data_dir', type=type(defaults.data_dir), default=defaults.data_dir, help=DATA_DIR)
    parser.add_argument('--model', type=type(defaults.model), default=defaults.model, help=MODEL)
    parser.add_argument('--model_dir', type=type(defaults.model_dir), default=defaults.model_dir, help=MODEL_DIR)
    parser.add_argument('--qa', type=type(defaults.qa), default=defaults.qa, help=QA)
    parser.add_argument('--qa_model', type=type(defaults.qa_model), default=defaults.qa_model, help=QA_MODEL)
    parser.add_argument('--qa_model_dir', type=type(defaults.qa_model_dir), default=defaults.qa_model_dir, help=QA_MODEL_DIR)
    parser.add_argument('--filter_results', type=type(defaults.filter_results), default=defaults.filter_results, help=FILTER_RESULTS)
    return parser
