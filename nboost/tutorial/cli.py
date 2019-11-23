
from nboost.tutorial import api
from typing import List
import argparse
import termcolor


def set_travel_parser(parser):
    """Travel tutorial args"""
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--port', type=int, default=9200, help='port of the proxy')


def main(argv: List[str] = None):
    """nboost-tutorial entrypoint"""
    name = termcolor.colored('NBoost OpenSource tutorial', 'cyan', attrs=['underline'])
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest='tutorial', title='nboost-tutorials',
                               description='Welcome to the %s.' % name)

    set_travel_parser(sp.add_parser('Travel', help='travel tutorial'))
    args = parser.parse_args(argv)
    tutorial = getattr(api, args.tutorial)(args)
    tutorial.setup()
    tutorial.run()
