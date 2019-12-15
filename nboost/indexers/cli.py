"""NBoost command line interface"""
from argparse import ArgumentParser
from typing import List, Type
from pathlib import Path
import termcolor
from nboost.indexers.base import BaseIndexer
from nboost.indexers.es import ESIndexer

TAG = termcolor.colored('NBoost Indexer', 'cyan', attrs=['underline'])
DESCRIPTION = ('This is the %s. This command line utility can be used to send '
               'a csv to a search api for indexing.' % TAG)

FILE = 'path of the csv to send to the index'
NAME = 'name of the index send to'
ID_COL = 'column number of the choice id'
BODY_COL = 'column number of the choice body'
FIELD_NAME = 'field name of the choice'
HOST = 'host of the search api server'
PORT = 'port of the server'
DELIM = 'csv delimiter'
SHARDS = 'number of index shards to create'
INDEXER = 'the indexer class'
VERBOSE = 'turn on detailed logging'


def set_parser() -> ArgumentParser:
    """Add default nboost-index cli arguments to a given parser"""
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--verbose', action='store_true', default=False, help=VERBOSE)
    parser.add_argument('--file', type=Path, default='.', help=FILE)
    parser.add_argument('--name', type=str, default='nboost', help=NAME)
    parser.add_argument('--id_col', type=int, default=0, help=ID_COL)
    parser.add_argument('--body_col', type=int, default=1, help=BODY_COL)
    parser.add_argument('--field_name', type=str, default='passage', help=FIELD_NAME)
    parser.add_argument('--host', type=str, default='0.0.0.0', help=HOST)
    parser.add_argument('--port', type=int, default=9200, help=PORT)
    parser.add_argument('--delim', type=str, default='\t', help=DELIM)
    parser.add_argument('--shards', default=3, type=int)
    parser.add_argument('--indexer', type=lambda x: ESIndexer, default='ESIndexer', help=INDEXER)
    parser.add_argument('--field', default='passage', type=str)
    return parser


def main(argv: List[str] = None):
    parser = set_parser()
    args = vars(parser.parse_args(argv))
    indexer = args.pop('indexer')  # type: Type[BaseIndexer]
    indexer(**args).index()


if __name__ == "__main__":
    main()
