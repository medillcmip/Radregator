"""Exceptions thrown throughout the core app."""

class UnknownOutputFormatException(Exception):
    """Exception thrown when an API call is made requesting output in
       an unknown format."""
    pass
