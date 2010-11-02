from fabric.api import env, require, run, cd 
from fabric.contrib.files import sed

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

def install_packages():
    require("instance", provided_by=[staging])
    require("base_dir", provided_by=[staging])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; pip install --requirement=conf/requirements.txt" % \
            (env.instance))

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

def git_pull(git_remote=None,git_branch=None):
    require("hosts", provided_by=[staging])
    require("instance", provided_by=[staging])
    require("git_remote", provided_by=[staging])
    require("git_branch", provided_by=[staging])
    if git_remote != None:
        env.git_remote = git_remote
    if git_branch != None:
        env.git_branch = git_branch
    run("cd %s/radregator; git pull %s %s" % \
        (env.base_dir, env.git_remote, env.git_branch))

def install_local_settings(db_password):
    require("hosts", provided_by=[staging])
    require("base_dir", provided_by=[staging])
    require("instance", provided_by=[staging])
    with cd("%s/radregator" % (env.base_dir)):
        sed("%s/radregator/conf/settings_local-%s.py" % \
            (env.base_dir, env.instance), 'FAB_REPL_DB_PASSWORD', \
            db_password)
        run("cp ./conf/settings_local-%s.py settings_local.py" % \
            (env.instance))

def syncdb():
    require("hosts", provided_by=[staging])
    require("base_dir", provided_by=[staging])
    require("instance", provided_by=[staging])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; ./manage.py syncdb --noinput" % (env.instance))

def migrate():
    require("hosts", provided_by=[staging])
    require("base_dir", provided_by=[staging])
    require("instance", provided_by=[staging])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; ./manage.py migrate core --noinput" % (env.instance))
        run("workon %s; ./manage.py migrate tagger --noinput" % (env.instance))
        run("workon %s; ./manage.py migrate clipper --noinput" % (env.instance))
        run("workon %s; ./manage.py migrate users --noinput" % (env.instance))

def install_apache_config():
    require("hosts", provided_by=[staging])
    require("base_dir", provided_by=[staging])
    require("instance", provided_by=[staging])
    with cd("%s/radregator" % (env.base_dir)):
        run("cp ./conf/httpd-%s.conf ../apache2/conf/httpd.conf" % \
            (env.instance))
