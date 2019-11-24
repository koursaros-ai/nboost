from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from nboost.cli import add_default_args
from nboost.benchmark import api
from nboost.proxy import Proxy
from typing import List
import termcolor
import requests

DATASETS = ['MsMarco']


def main(argv: List[str] = None):
    name = termcolor.colored('NBoost Benchmarker', 'cyan', attrs=['underline'])
    parser = ArgumentParser(
        description='This is the %s for nboost, a search-api-boosting platform'
                    'Use the cli as normal, but instead of hosting a proxy,'
                    'the cli will benchmark speed and efficacy on a specified '
                    'dataset.' % name,
        formatter_class=ArgumentDefaultsHelpFormatter)

    add_default_args(parser)
    parser.add_argument('--rows', type=int, default=-1, help='number of rows for benchmarking')
    parser.add_argument('--dataset', type=str, required=True, choices=DATASETS)
    parser.add_argument('--topk', type=int, default=10)
    parser.add_argument('--url', default=None, type=str)
    parser.add_argument('--shards', default=1, type=str)
    args = parser.parse_args(argv)

    if args.dataset == 'msmarco':
        args.field = 'passage'

    proxy = Proxy(**vars(args))
    proxy.start()
    # execute dataset dependencies
    benchmarker = getattr(api, args.dataset)(args)
    benchmarker.benchmark()

    print(requests.get('http://localhost:8000/nboost').text)
    print()
    proxy.close()
    print('DONE')


if __name__ == "__main__":
    main()
