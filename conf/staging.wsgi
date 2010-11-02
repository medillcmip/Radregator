import os
import site
import sys

# add the virtual environment path
site.addsitedir('/home/medill2010/virtualenvs/staging/lib/python2.6/site-packages')

# fix markdown.py (and potentially others) using stdout
sys.stdout = sys.stderr

# Calculate the path based on the location of the WSGI script.
conf = os.path.dirname(__file__)
project = os.path.dirname(conf)
workspace = os.path.dirname(project) 
sys.path.append(workspace)

os.environ['DJANGO_SETTINGS_MODULE'] = 'radregator.settings'
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
