"""NBoost command line interface"""
from argparse import ArgumentParser
from typing import List, Type
import termcolor
from nboost.indexers.base import BaseIndexer
from nboost.helpers import import_class
from nboost.indexers import defaults
from nboost.maps import INDEXER_MAP


TAG = termcolor.colored('NBoost Indexer', 'cyan', attrs=['underline'])
DESCRIPTION = ('This is the %s. This command line utility can be used to send '
               'a csv to a search api for indexing.' % TAG)

FILE = 'path of the csv to send to the index'
INDEX_NAME = 'name of the index send to'
ID_COL = 'whether to index each doc with an id (should be first col in csv)'
HOST = 'host of the search api server'
PORT = 'port of the server'
DELIM = 'csv delimiter'
SHARDS = 'number of index shards to create'
INDEXER = 'the indexer class'
VERBOSE = 'turn on detailed logging'


def set_parser() -> ArgumentParser:
    """Add default nboost-index cli arguments to a given parser"""
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--verbose', type=type(defaults.verbose), default=defaults.verbose, help=VERBOSE)
    parser.add_argument('--file', type=type(defaults.file), default=defaults.file, help=FILE)
    parser.add_argument('--index_name', type=type(defaults.index_name), default=defaults.index_name, help=INDEX_NAME)
    parser.add_argument('--host', type=type(defaults.host), default=defaults.host, help=HOST)
    parser.add_argument('--port', type=type(defaults.port), default=defaults.port, help=PORT)
    parser.add_argument('--delim', type=type(defaults.delim), default=defaults.delim, help=DELIM)
    parser.add_argument('--shards', type=type(defaults.shards), default=defaults.shards)
    parser.add_argument('--id_col', action='store_true', help=ID_COL)
    parser.add_argument('--indexer', type=type(defaults.indexer), default=defaults.indexer, help=INDEXER)
    return parser


def main(argv: List[str] = None):
    parser = set_parser()
    args = vars(parser.parse_args(argv))
    indexer_class = args.pop('indexer')
    indexer_module = INDEXER_MAP[indexer_class]
    indexer = import_class(indexer_module, indexer_class)  # type: Type[BaseIndexer]
    indexer(**args).index()


if __name__ == "__main__":
    main()
