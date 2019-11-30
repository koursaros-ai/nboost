from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import List
import termcolor
import requests
from nboost.benchmark.benchmarker import Benchmarker
from nboost.cli import set_parser
from nboost.proxy import Proxy
from nboost import DATASET_MAP


def main(argv: List[str] = None):
    name = termcolor.colored('NBoost Benchmarker', 'cyan', attrs=['underline'])
    parser = set_parser()
    parser.description = (
                    'This is the %s for nboost, a search-api-boosting platform'
                    'Use the cli as normal, but instead of hosting a proxy,'
                    'the cli will benchmark speed and efficacy on a specified '
                    'dataset.' % name
    )

    parser.add_argument('--rows', type=int, default=-1, help='number of rows for benchmarking')
    parser.add_argument('--connector', type=str, default='ESConnector')
    parser.add_argument('--dataset', type=str, required=True, choices=DATASET_MAP.keys())
    parser.add_argument('--topk', type=int, default=10)
    parser.add_argument('--url', default=None, type=str)
    parser.add_argument('--field', default='passage', type=str)
    parser.add_argument('--shards', default=1, type=int)
    args = parser.parse_args(argv)
    proxy = Proxy(**vars(args))
    proxy.start()

    benchmarker = Benchmarker(**vars(args))
    benchmarker.setup()
    benchmarker.benchmark()

    print(requests.get('http://localhost:8000/nboost').text)
    print()
    proxy.close()
    print('DONE')


if __name__ == "__main__":
    main()
