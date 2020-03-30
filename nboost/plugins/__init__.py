"""Base Plugin module"""
from nboost.delegates import RequestDelegate, ResponseDelegate
from nboost.database import DatabaseRow
from nboost.helpers import import_class
from nboost.maps import MODULE_MAP


def resolve_plugin(plugin, **cli_args):
    model = import_class(MODULE_MAP[plugin], plugin)
    return model(**cli_args)


class Plugin:
    """A plugin has two callbacks, one on request and one on response. Each
    callback, the plugin can get and set the respective messages. The plugin
    can also add a value to the database row which show up in queries
    to the /nboost/status path"""
    def __init__(self, **cli_args):
        """Configure using command line args"""

    @property
    def configs(self):
        """Returns configs to be displayed on /nboost/status"""
        return {}

    def on_request(self, request: RequestDelegate, db_row: DatabaseRow):
        """Access request."""

    def on_response(self, response: ResponseDelegate, db_row: DatabaseRow):
        """Access response."""
