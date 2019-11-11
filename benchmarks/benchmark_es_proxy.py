from resources.es.shakespeare import ensure_shakespeare_elasticsearch
from nboost.cli import create_proxy
from statistics import mean
import requests
import time


def benchmark_es_proxy():

    query = 'shakespeare/_search?q=text_entry:palace'
    proxy = create_proxy()
    ensure_shakespeare_elasticsearch(
        host=proxy.kwargs['ext_host'],
        port=proxy.kwargs['ext_port']
    )
    proxy.start()

    times = [[], []]
    for i in range(proxy.kwargs['laps']):

        _1 = time.perf_counter()

        requests.get('http://%s:%s/%s' % (
            proxy.kwargs['host'],
            proxy.kwargs['port'],
            query))

        _2 = time.perf_counter()

        requests.get('http://%s:%s/%s' % (
            proxy.kwargs['ext_host'],
            proxy.kwargs['ext_port'],
            query))

        _3 = time.perf_counter()
        times[0].append(_2-_1)
        times[1].append(_3-_2)

    t1, t2 = mean(times[0]) * 10 ** 3, mean(times[1]) * 10 ** 3
    # print(requests.get('http://localhost:9000/status').text)
    print()
    print('Proxy avg: %s ms; Server avg %s ms' % (t1, t2))
    proxy.close()
    print('DONE')


if __name__ == '__main__':
    benchmark_es_proxy()
