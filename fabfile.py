from fabric.api import *
from fabric.contrib.console import confirm

# Global configuration variables
WEBFACTION_HOME = '/home/medill2010'
WEBFACTION_APPS = WEBFACTION_HOME + '/webapps'

def staging():
    env.hosts = ['medill2010.webfactional.com']
    env.user = 'medill2010'
    env.base_dir = WEBFACTION_APPS + '/radregator_staging'
    env.instance = 'staging'
    env.database = 'medill2010_radregator_staging'
    env.git_repo = 'git@github.com:medillcmip/Radregator.git' 
    env.git_remote = 'origin'
    env.git_branch = 'master'

def mkvirtualenv():
    """
    Create the virtualenv for the deployment.
    """
    require("hosts", provided_by=[staging])
    require("instance", provided_by=[staging])
    run("mkvirtualenv %s" % (env.instance))

def rmvirtualenv():
    """
    Delete the virtualenv for the deployment.
    """
    require("hosts", provided_by=[staging])
    require("instance", provided_by=[staging])
    run("rmvirtualenv %s" % (env.instance))

def git_clone():
    """
    Clone the repo for the project.
    """
    require("hosts", provided_by=[staging])
    require("instance", provided_by=[staging])
    require("git_repo", provided_by=[staging])
    run("cd %s; git clone %s radregator" % (env.base_dir, env.git_repo))

def rmrepo():
    require("hosts", provided_by=[staging])
    require("instance", provided_by=[staging])
    run("cd %s; rm -rf radregator" % (env.base_dir))

def git_pull():
    require("hosts", provided_by=[staging])
    require("instance", provided_by=[staging])
    require("git_remote", provided_by=[staging])
    require("git_branch", provided_by=[staging])
    run("cd %s/radregator; git pull %s %s" % \
        (env.base_dir, env.git_remote, env.git_branch))
