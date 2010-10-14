"""Utility functions that may be used throughout the core application."""

import re

def slugify(s):
    p = re.compile('\W') # match non-alphanumeric characters 
    new_s = p.sub('-', s) # and replace them with '-'
    new_s = new_s.lower() # and then convert to lowercase

    return new_s
