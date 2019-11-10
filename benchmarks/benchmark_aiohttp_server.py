from nboost.server import AioHttpServer
from nboost.cli import create_proxy
from nboost.paths import RESOURCES
from nboost.base.types import *
from pprint import pprint
import json as JSON
import requests


def main():
    json = RESOURCES.joinpath('es_result.json').read_bytes()

    async def search(req):
        return Response({}, json, 200)

    async def only_on_server_get(req):
        return Response({}, json, 200)

    async def only_on_server_post(req):
        return Response({}, req.body, 200)

    server = AioHttpServer(port=10000, verbose=True)
    server.create_app([
        ({'/search': ['GET']}, search),
        ({'/only_on_server_get': ['GET']}, only_on_server_get),
        ({'/only_on_server_post': ['POST']}, only_on_server_post),
    ], not_found_handler=lambda x: print(x))

    server.start()
    server.is_ready.wait()
    proxy = create_proxy([
        '--codex', 'TestCodex',
        '--model', 'TestModel',
        '--port', '9000',
        '--ext_port', '10000',
        '--field', 'description',
        '--multiplier', '2',
        '--verbose'
    ])
    proxy.start()

    res = requests.get('http://localhost:9000/search')
    print(res.content)

    res = requests.get('http://localhost:9000/only_on_server_get')
    print(res.content)

    res = requests.post('http://localhost:9000/only_on_server_post', data=json)
    print(res.content)

    res = requests.get('http://localhost:9000/status')
    print(res.text)
    proxy.close()
    server.stop()
    server.join()
    print('DONE')


if __name__ == '__main__':
    main()
