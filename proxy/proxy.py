from termcolor import colored

from ..utils import set_logger
import itertools
import asyncio
import requests
from aiohttp import web
from ..es import clients
from ..models import *



class RankProxy:
    def __init__(self, args):
        self.args = args

    def create_site(self):
        with DistilbertModel(max_concurrency=self.args.http_max_connect,
                             port=self.args.port, port_out=self.args.es_port) as model:

            logger = set_logger(colored('PROXY', 'red'))
            query_id = itertools.count()
            train_id = itertools.count()
            loop = asyncio.get_event_loop()
            es_client = getattr(es_clients, self.args.es_client)(self.args)

            def exception(ex):
                return web.json_response(
                    dict(error=str(ex), type=type(ex).__name__), status=400)

            async def status(request):
                return model.status

            async def query(request):
                logger.info('new query request from %s' % request.remote_addr)
                try:
                    async for line in request.content:
                        hits = es_client.
                        res = model.query(line)
                        return web.json_response(dict(res=res))

                except Exception as ex:
                    logger.error('Error handling query request', exc_info=True)
                    return exception(ex)

            async def train(request):
                logger.info('new train request from %s' % request.remote_addr)
                try:
                    async for line in request.content:
                        res = model.train(train)
                        return web.json_response(dict(res=res))

                except Exception as ex:
                    logger.error('Error handling train request', exc_info=True)
                    return exception(ex)

            async def main():
                app = web.Application()
                app.add_routes([
                    web.post('/train', train),
                    web.post('/status', status),
                    web.post('/query', query)
                ])
                runner = web.AppRunner(app)
                await runner.setup()
                site = web.TCPSite(runner, self.args.host, self.args.port)
                await site.start()

                logger.info('http server forwarding port %d to %d' % (
                    self.args.port,
                    self.args.es_port))

            loop.run_until_complete(main())
            loop.run_forever()

    def run(self):
        self.create_site()
