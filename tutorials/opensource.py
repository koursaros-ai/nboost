from typing import List
import argparse
import termcolor


def main(argv: List[str] = None):
    name = termcolor.colored('NBoost OpenSource tutorial', 'cyan', attrs=['underline'])
    parser = argparse.ArgumentParser(
        description='Welcome to the %s. Please input the '
                    'host (--host) and port (--port) of the Elasticsearch  '
                    'server that you wish to send the dataset to.' % name,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='host of the proxy')
    parser.add_argument('--port', type=int, default=8000,
                        help='port of the proxy')
    args = parser.parse_args(argv)


