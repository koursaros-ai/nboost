class TestModel(object):

    def __init__(self, args):
        pass

    def train(self, query, candidates, labels):
        pass

    def rank(self, query, candidates, k):
        return range(0, k)