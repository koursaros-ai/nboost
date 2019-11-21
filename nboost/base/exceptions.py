"""NBoost base exceptions"""


class RequestException(Exception):
    """Exception when receiving client request"""


class StatusRequest(RequestException):
    """Client sent status request"""


class UnknownRequest(RequestException):
    """Unrecognized url path in request"""


class MissingQuery(RequestException):
    """Could not parse query in request"""
