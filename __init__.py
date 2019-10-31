from .clients.test import TestClient
from .clients.multisearch import MutliSearchClient
from .models.distilbert import DBRank
from .models.test import TestModel
from .proxies.rank import RankProxy

clients = {
    TestClient.__name__: TestClient,
    MutliSearchClient.__name__: MutliSearchClient
}

models = {
    DBRank.__name__: DBRank,
    TestModel.__name__: TestModel
}

proxies = {
    RankProxy.__name__,
}