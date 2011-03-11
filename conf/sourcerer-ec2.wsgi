import os
import site
import sys

# fix markdown.py (and potentially others) using stdout
sys.stdout = sys.stderr

# Calculate the path based on the location of the WSGI script.
#conf = os.path.dirname(__file__)
#project = os.path.dirname(conf)
#workspace = os.path.dirname(project) 
#sys.path.append(workspace)
sys.path.append('/var/sourcerer')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
