"""Utility functions that may be used throughout the core application."""

import re
import logging
from django.conf import settings
from django.db import models, connection
import re
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup, Comment

def sanitize_html(value, base_url=None):
    '''
    http://stackoverflow.com/questions/16861/sanitising-user-input-using-python
    in response to issue 117 we need greater validation in some cases
    so that we aren't rendering HTML in parts of the page
    '''
    rjs = r'[\s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[\s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    #currently we aren't allowing any formatting in the forms so 
    #uncomment the next two lines to add support for html input 
    #on Q&A submission
    #validTags = 'p i strong b u a h1 h2 h3 pre br'.split()
    #validAttrs = 'href src width height'.split()
    validTags = ''.split()
    validAttrs = ''.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')

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
    #logger = get_logger();
    #logger.debug("entering function comment_cmp_default()");
    return comment_cmp_stack(comm1, comm2, \
                             (comment_cmp_is_reporter, comment_cmp_clips, \
                              comment_cmp_upvotes, comment_cmp_date_desc))

def comment_cmp_date_first(comm1, comm2):
    """
    Compare comments by created date first, then by some other stuff.

    """
    #logger = get_logger();
    #logger.debug("entering function comment_cmp_date_first()");
    return comment_cmp_stack(comm1, comm2, \
                             (comment_cmp_date_desc, comment_cmp_is_reporter, \
                              comment_cmp_clips, comment_cmp_upvotes))

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


class SQLCountIfConcur(models.sql.aggregates.Aggregate):
    is_ordinal = True
    sql_function = 'COUNT'
    """
    NOTE: http://developer.postgresql.org/pgdocs/postgres/sql-syntax-lexical.html
    POSTGRESql requires constants to be delimited by single quote values
    """
    sql_template= '%(function)s (CASE WHEN "core_commentresponse"."type" LIKE \'concur\' THEN 1 ELSE NULL END)'


class CountIfConcur(models.Aggregate):
    """Custom Aggregate class to count "concur" (up vote) responses.
    
    This is based on the work described at 
    http://www.voteruniverse.com/Members/jlantz/blog/conditional-aggregates-in-django
    However, I was not able to use the more general code described in this blog
    post, perhaps because django.db.sql.models.where.WhereNode.as_sql()'s 
    implementation has changed, or because I'm using a ManyToMany relation
    and the example is a ForeignKey relation.  In the interest of expediency, I
    just hardcoded the test.

    The thread at
    http://groups.google.com/group/django-users/browse_thread/thread/bd5a6b329b009cfa?pli=1 
    has good information about implementing custom Aggregate classes in general.
    
    """
    name = 'COUNT'

    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = SQLCountIfConcur(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate
