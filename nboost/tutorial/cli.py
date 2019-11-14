
from nboost.tutorial import api
from typing import List
import argparse
import termcolor


def set_opensource_parser(parser):
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--port', type=int, default=9200, help='port of the proxy')


def set_another_tutorial_parser(parser):
    pass


def main(argv: List[str] = None):
    adf = argparse.ArgumentDefaultsHelpFormatter
    name = termcolor.colored('NBoost OpenSource tutorial', 'cyan', attrs=['underline'])
    parser = argparse.ArgumentParser(formatter_class=adf)

    sp = parser.add_subparsers(dest='tutorial', title='nboost-tutorials',
                               description='Welcome to the %s. Please input the '
                                           'host (--host) and port (--port) of the Elasticsearch  '
                                           'server that you wish to send the dataset to.' % name,)

    set_opensource_parser(sp.add_parser('opensource', help='opensource parser tutorial', formatter_class=adf))
    set_another_tutorial_parser(sp.add_parser('demo', help='example tutorial stub', formatter_class=adf))

    args = parser.parse_args(argv)
    getattr(api, args.tutorial)(args)

