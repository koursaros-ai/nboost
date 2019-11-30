"""NBoost base exceptions"""


class RequestException(Exception):
    """Exception when receiving client request"""


class ResponseException(Exception):
    """Upstream response contains error message"""


class UpstreamConnectionError(ConnectionRefusedError):
    """Raised when the upstream host refuses connection"""


class StatusRequest(RequestException):
    """Client sent status request"""


class UnknownRequest(RequestException):
    """Unrecognized url path in request"""


class MissingQuery(RequestException):
    """Could not parse query in request"""
