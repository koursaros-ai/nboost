"""NBoost base exceptions"""


class RequestException(Exception):
    """Exception when receiving client request"""


class ResponseException(Exception):
    """Upstream response contains error message"""


class UpstreamConnectionError(Exception):
    """Raised when the upstream host refuses connection"""


class StatusRequest(RequestException):
    """Client sent status request"""


class FrontendRequest(RequestException):
    """Client sent frontend request"""


class UnknownRequest(RequestException):
    """Unrecognized url path in request"""


class MissingQuery(RequestException):
    """Could not parse query in request"""


class UpstreamServerError(ResponseException):
    """Raised when the upstream server sends an error status code."""


class InvalidChoices(ResponseException):
    """The length of choices, choice ids, and choice values must be the same"""
