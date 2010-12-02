"""Utility functions that may be used throughout the core application."""

import re
import logging
from django.conf import settings
from django.db import models

def build_readable_errors(errordict):
    """ Translate an error dictionary into HTML, to return to Ajax code """
    retstr = ''
    for field, errors in errordict.iteritems():
        retstr += '<p>%s: %s </p>' % (field, ';'.join(errors))

    return retstr
        

def comment_cmp(comm1, comm2):
    
    # Reporter comments take priority

    if comm1.user.is_reporter() and not comm2.user.is_reporter():
        return -1

    if comm2.user.is_reporter() and not comm1.user.is_reporter():
        return 1

    # Then comments with clips
    if comm1.clips and not comm2.clips: return -1
    
    if comm2.clips and not comm1.clips: return 1
    
    # Then comments with more upvotes
    return cmp(comm2.responses.count(), comm1.responses.count())



def slugify(s):
    p = re.compile('\W') # match non-alphanumeric characters 
    new_s = p.sub('-', s) # and replace them with '-'
    new_s = new_s.lower() # and then convert to lowercase

    return new_s

def get_logger():
    """Configure logging.
     
       Thanks http://djangosnippets.org/snippets/16/  
    
    """
    
    # create logger
    logger = logging.getLogger() 

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    if settings.DEBUG:
        # If we're in DEBUG mode, set log level to DEBUG
        logger.setLevel(logging.DEBUG) 

    return logger

# Implement a conditional aggregate
# Via http://paste.pocoo.org/show/123690/ and
# http://www.voteruniverse.com/Members/jlantz/blog/conditional-aggregates-in-django

#class SQLCountIf(models.sql.aggregates.Aggregate):
    #is_ordinal = True
    #sql_function = 'COUNT'
    #sql_template= '%(function)s(CASE %(condition)s WHEN true THEN 1 ELSE NULL END)'
#
#class CountIf(models.Aggregate):
    #name = 'COUNT'
#
    #def add_to_query(self, query, alias, col, source, is_summary):
        #sql, params = query.model._default_manager.filter(**self.extra['condition']).query.where.as_sql()
        #self.extra['condition'] = sql % tuple(params)
        #aggregate = SQLCountIf(col, source=source, is_summary=is_summary, **self.extra)
        #query.aggregates[alias] = aggregate
