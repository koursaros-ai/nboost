from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from nboost.cli import add_default_args
from nboost.proxy import Proxy
from statistics import mean
from typing import List
import termcolor
import requests
import time


def main(argv: List[str] = None):
    name = termcolor.colored('NBoost Benchmarker', 'cyan', attrs=['underline'])
    parser = ArgumentParser(
        description='This is the %s for nboost, a search-api-boosting platform'
                    'Use the cli as normal, but instead of hosting a proxy,'
                    'the cli will benchmark speed and efficacy using the '
                    'MSMARCO dataset.' % name,
        formatter_class=ArgumentDefaultsHelpFormatter)

    add_default_args(parser)
    parser.add_argument('--laps', action='store_true', default=False, help='number of laps for benchmarking')
    args = parser.parse_args(argv)
    proxy = Proxy(**vars(args))

    # TODO (jack): add script to dump MSMARCO to ext_host:ext_port

    proxy.start()

    times = [[], []]
    for i in range(proxy.kwargs['laps']):

        _1 = time.perf_counter()

        proxy_res = requests.get('http://%s:%s/%s' % (
            proxy.kwargs['host'],
            proxy.kwargs['port'],
            query))

        _2 = time.perf_counter()

        direct_res = requests.get('http://%s:%s/%s' % (
            proxy.kwargs['ext_host'],
            proxy.kwargs['ext_port'],
            query))

        _3 = time.perf_counter()
        times[0].append(_2-_1)
        times[1].append(_3-_2)

    proxy_avg = mean(times[0]) * 10 ** 3
    server_avg = mean(times[1]) * 10 ** 3
    print(requests.get('http://localhost:9000/status').text)
    print()
    print('Proxy avg: %s ms; Server avg %s ms' % (proxy_avg, server_avg))
    proxy.close()
    print('DONE')
