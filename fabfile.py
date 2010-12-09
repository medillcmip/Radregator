from fabric.api import env, require, run, cd, local 
from fabric.contrib.files import sed

# Global configuration variables
WEBFACTION_HOME = '/home/medill2010'
WEBFACTION_APPS = WEBFACTION_HOME + '/webapps'

def staging():
    env.hosts = ['medill2010.webfactional.com']
    env.user = 'medill2010'
    env.base_dir = WEBFACTION_APPS + '/radregator_staging'
    env.instance = 'staging'
    env.git_repo = 'git@github.com:medillcmip/Radregator.git' 
    env.git_remote = 'origin'
    env.git_branch = 'master'


def production():
    env.hosts = ['medill2010.webfactional.com']
    env.user = 'medill2010'
    env.base_dir = WEBFACTION_APPS + '/radregator_production'
    env.instance = 'production'
    env.git_repo = 'git@github.com:medillcmip/Radregator.git' 
    env.git_remote = 'origin'
    env.git_branch = 'master'


def testing(instance_num):
    env.hosts = ['medill2010.webfactional.com']
    env.user = 'medill2010'
    env.base_dir = WEBFACTION_APPS + '/radregator_testing_' + instance_num
    env.instance = 'testing_' + instance_num
    env.git_repo = 'git@github.com:medillcmip/Radregator.git' 
    env.git_remote = 'origin'
    #env.git_branch = 'testing'
    env.git_branch = 'master'


def mkinstance(db_password, fb_api_id, fb_api_key, fb_secret_key):
    """
    Create a deployment instance from scratch.
    """
    mkvirtualenv()
    git_clone()
    install_packages()
    install_local_settings(db_password, fb_api_id, fb_api_key, fb_secret_key)
    syncdb()
    migrate()
    loaddata()
    install_apache_config()

def rminstance():
    """
    Delete a deployment instance created with mkinstance.
    """
    drop_tables()
    rmrepo()
    rmvirtualenv()

def deploy(db_password, fb_api_id, fb_api_key, fb_secret_key):
    """
    Deploy most recent code into a deployment instance created with mkinstance.
    """
    git_pull()
    install_local_settings(db_password, fb_api_id, fb_api_key, fb_secret_key)
    syncdb()
    migrate()
    loaddata()
    install_apache_config()
    
def mkvirtualenv():
    """
    Create the virtualenv for the deployment.
    """
    require("hosts", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    run("mkvirtualenv --no-site-packages %s" % (env.instance))

def rmvirtualenv():
    """
    Delete the virtualenv for the deployment.
    """
    require("hosts", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    run("rmvirtualenv %s" % (env.instance))

def install_packages():
    require("instance", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        # egenix-mx-base doesn't like to be installed with pip in a 
        # --no-site-packages virtualenv
        run("workon %s; easy_install `grep egenix-mx-base ./conf/requirements.txt`" % \
            (env.instance))
        run("workon %s; pip install --requirement=./conf/requirements.txt" % \
            (env.instance))

def reinstall_virtualenv():
    require("instance", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    rmvirtualenv()
    mkvirtualenv()
    install_packages()

def git_clone():
    """
    Clone the repo for the project.
    """
    require("hosts", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    require("git_repo", provided_by=[staging, production, testing])
    run("cd %s; git clone %s radregator" % (env.base_dir, env.git_repo))

def rmrepo():
    require("hosts", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    run("cd %s; rm -rf radregator" % (env.base_dir))

def git_pull(git_remote=None,git_branch=None):
    require("hosts", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    require("git_remote", provided_by=[staging, production, testing])
    require("git_branch", provided_by=[staging, production, testing])
    if git_remote != None:
        env.git_remote = git_remote
    if git_branch != None:
        env.git_branch = git_branch
    run("cd %s/radregator; git pull %s %s" % \
        (env.base_dir, env.git_remote, env.git_branch))

def install_local_settings(db_password, fb_api_id, fb_api_key, fb_secret_key):
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        sed("%s/radregator/conf/settings_local-%s.py" % \
            (env.base_dir, env.instance), 'FAB_REPL_DB_PASSWORD', \
            db_password)
        sed("%s/radregator/conf/settings_local-%s.py" % \
            (env.base_dir, env.instance), 'FAB_REPL_FB_API_ID', \
            fb_api_id)
        sed("%s/radregator/conf/settings_local-%s.py" % \
            (env.base_dir, env.instance), 'FAB_REPL_FB_API_KEY', \
            fb_api_key)
        sed("%s/radregator/conf/settings_local-%s.py" % \
            (env.base_dir, env.instance), 'FAB_REPL_FB_SECRET_KEY', \
            fb_secret_key)
        run("cp ./conf/settings_local-%s.py settings_local.py" % \
            (env.instance))

def syncdb():
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; ./manage.py syncdb --noinput" % (env.instance))

def migrate():
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; ./manage.py migrate" % (env.instance))

def loaddata():
    """
    Load fixture data.

    Note: You need to create a ~/.pgpass file so ./manage.py dbshell doesn't
    require entering a password.
    """
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        # HACK ALERT: South doesn't play well with the initial data.  
        # Need to empty these tables first or you get an error.
        run("workon %s; echo 'DELETE FROM auth_group_permissions; DELETE FROM auth_permission; DELETE FROM django_admin_log; DELETE FROM django_content_type;' |./manage.py dbshell" % (env.instance))
        run("workon %s; ./manage.py loaddata ./fixtures/starting_data.json" % (env.instance))

def dev_loaddata():
    """
    Load fixture data into a local development instance.
    """
    local("echo 'DELETE FROM auth_group_permissions; DELETE FROM auth_permission; DELETE FROM django_admin_log; DELETE FROM django_content_type;' | ./manage.py dbshell")
    local("./manage.py loaddata ./fixtures/starting_data.json")

def compilemessages():
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; ./manage.py compilemessages" % (env.instance))

def drop_tables():
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        run("workon %s; echo \"select 'DROP table ' || quote_ident(table_schema) || '.' || quote_ident(table_name) || ' CASCADE;' from information_schema.tables where table_type = 'BASE TABLE' and not table_schema ~ '^(information_schema|pg_.*)$'\" | ./manage.py dbshell | head --lines=-2 | ./manage.py dbshell " % (env.instance))


def install_apache_config():
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    with cd("%s/radregator" % (env.base_dir)):
        run("cp ./conf/httpd-%s.conf ../apache2/conf/httpd.conf" % \
            (env.instance))

def restart():
    require("hosts", provided_by=[staging, production, testing])
    require("base_dir", provided_by=[staging, production, testing])
    require("instance", provided_by=[staging, production, testing])
    with cd("%s" % (env.base_dir)):
        run("./apache2/bin/restart")
