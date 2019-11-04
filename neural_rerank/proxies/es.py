from .base import BaseProxy
from ..clients import ESClient
from ..models import TestModel


class ESProxy(BaseProxy, ESClient, TestModel):
    _search_path = '/{index}/_search'
