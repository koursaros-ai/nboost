from .base import BaseProxy

class TestProxy(BaseProxy):

    def status(self):
        return 'Hello world!'

    def train(self, request):
        print('Recieved train request')
        return request