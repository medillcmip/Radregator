"""Exceptions thrown throughout the core app."""

class UnknownOutputFormatException(Exception):
    """Exception thrown when an API call is made requesting output in
       an unknown format."""
    pass

class NonAjaxRequest(Exception):
    """Exception thrown when an API call is made that is not an AJAX request
       and we don't want to allow this kind of (potentially) cross-site 
       call"""
    pass
