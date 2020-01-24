from nboost.plugins import Plugin
from nboost.delegates import ResponseDelegate
from nboost.database import DatabaseRow


class DebugPlugin(Plugin):
    """Adds the request and parsed server response values to the response."""
    def on_response(self, response: ResponseDelegate, db_row: DatabaseRow):
        response.set_path('body.nboost.topk', db_row.topk)
        response.set_path('body.nboost.topn', response.request.topn)
        response.set_path('body.nboost.query', response.request.query)
        response.set_path('body.nboost.choices', response.choices)
        response.set_path('body.nboost.cids', response.cids)
        response.set_path('body.nboost.cvalues', response.cvalues)

