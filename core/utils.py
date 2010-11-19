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
        
def comment_cmp_date_desc(comm1, comm2):
    if comm1.date_created > comm2.date_created:
        return -1
    elif comm1.date_created < comm2.date_created:
        return 1
    else:
        return 0

def comment_cmp_date_asc(comm1, comm2):
    if comm1.date_created > comm2.date_created:
        return 1
    elif comm1.date_created < comm2.date_created:
        return -1
    else:
        return 0

def comment_cmp_is_reporter(comm1, comm2):
    if comm1.user.is_reporter() and not comm2.user.is_reporter():
        return -1
    elif comm2.user.is_reporter() and not comm1.user.is_reporter():
        return 1
    else: 
        return 0

def comment_cmp_clips(comm1, comm2):
    if comm1.clips and not comm2.clips: 
        return -1
    elif comm2.clips and not comm1.clips: 
        return 1
    else:
        return 0

def comment_cmp_upvotes(comm1, comm2):
    return cmp(comm2.responses.count(), comm1.responses.count())

def comment_cmp_stack(comm1, comm2, cmp_functions):
    for cmp_function in cmp_functions:
        cmp_val = cmp_function(comm1, comm2)
        if cmp_val != 0:
            return cmp_val

def comment_cmp_default(comm1, comm2):
    """ 
    Default comparison function for comments. 
    
    It compares comments based on these factors (from most important to
    least important):

    1. Whether the comment poster was a reporter.
    2. The number of clips attached to a comment.
    3. The number of upvotes on a comment.
    4. The date the comment was created.
    """
    return comment_cmp_stack(comm1, comm2, \
                             (comment_cmp_is_reporter, comment_cmp_clips, \
                              comment_cmp_upvotes, comment_cmp_date_desc))


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
