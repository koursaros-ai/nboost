"""NBoost command line interface"""

import importlib
from pathlib import Path
from argparse import ArgumentParser
import termcolor
from nboost.maps import CLASS_MAP, CONFIG_MAP
from nboost.__version__ import __doc__
from nboost import PKG_PATH


TAG = termcolor.colored('NBoost (v%s)' % __doc__, 'cyan', attrs=['underline'])
DESCRIPTION = ('%s: is a scalable, search-api-boosting platform for '
               'developing and deploying SOTA models to improve the '
               'relevance of search results..' % TAG)
QA_MODEL = 'adds the qa plugin which treats the query as a question and marks the answer offset'
DELIM = 'the deliminator to concatenate multiple queries into a single query'
QA_MODEL_DIR = 'name or directory of the finetuned qa model'
CONFIG = 'which search api nboost should be configured for'
BATCH_SIZE = 'batch size for running through rerank model'
MODEL_DIR = 'name or directory of the finetuned model'
WORKERS = 'number of threads serving the proxy'
MULTIPLIER = 'factor to increase results by'
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


def set_parser() -> ArgumentParser:
    """Add default nboost cli arguments to a given parser"""
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--verbose', action='store_true', default=False, help=VERBOSE)
    parser.add_argument('--host', type=str, default='0.0.0.0', help=HOST)
    parser.add_argument('--port', type=int, default=8000, help=PORT)
    parser.add_argument('--uhost', type=str, default='0.0.0.0', help=UHOST)
    parser.add_argument('--uport', type=int, default=9200, help=UPORT)
    parser.add_argument('--delim', type=str, default='. ', help=DELIM)
    parser.add_argument('--lr', type=float, default=10e-3, help=LR)
    parser.add_argument('--max_seq_len', type=int, default=64, help=MAX_SEQ_LEN)
    parser.add_argument('--bufsize', type=int, default=2048, help=BUFSIZE)
    parser.add_argument('--batch_size', type=int, default=4, help=BATCH_SIZE)
    parser.add_argument('--multiplier', type=int, default=5, help=MULTIPLIER)
    parser.add_argument('--workers', type=int, default=10, help=WORKERS)
    parser.add_argument('--data_dir', type=Path, default=PKG_PATH.joinpath('.cache'), help=DATA_DIR)
    parser.add_argument('--config', type=str, default='elasticsearch', choices=CONFIG_MAP.keys(), help=CONFIG)
    parser.add_argument('--model', type=str, default='', help=MODEL)
    parser.add_argument('--model_dir', type=str, default='pt-bert-base-uncased-msmarco', help=MODEL_DIR)
    parser.add_argument('--qa', type=bool, default=False, help=QA)
    parser.add_argument('--qa_model', type=str, default='', help=QA_MODEL)
    parser.add_argument('--qa_model_dir', type=str, default='distilbert-base-uncased-distilled-squad', help=QA_MODEL_DIR)
    return parser



