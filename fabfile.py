'''
Open-Knesset fabfile. Usage:

$ fab [dev|live] setup deploy # for the first time
$ fab [dev|live] deploy # to run the latest version
'''
# Default release is 'current'
from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

env.repository = 'git://github.com/daonb/Open-Knesset.git'

def dev(port=80):
    """Staging server settings"""
    env.path = '/usr/local/src/dev.oknesset'
    env.hosts = ['dev.oknesset.org:%s' % port]

def live(port=80):
    """Production server settings"""
    env.path = '/usr/local/src/oknesset'
    env.hosts = ['oknesset.org:%s' % port]

def setup():
    """
    Setup a fresh env and install everything we need so it's ready to deploy to
    """
    run('mkdir -p %s' % env.path)
    clone_repo()

def deploy(fork='ofri', branch='master'):
    """Deploy the latest version of the site to the server and restart apache"""
    update(fork, branch)
    install_env()
    refresh_server()

def clone_repo():
    """Do initial clone of the git repo"""
    with cd(env.path):
        run('git clone %(repository) .' % env)
        run('python bootstrap.py')

def update(fork='ofri', branch='master'):
    """Pull the latest code into the git repo and copy to a timestamped release directory"""
    with cd(env.path):
        run('git pull %s %s' % (fork, branch))
        run('bin/buildout install lastbuild')

def refresh_env():
    with cd(env.path):
        run('bin/buildout')
        run('bin/django syncdb --migrate')

def install_env():
    """Install the required packages using buildout"""
    with cd(env.path):
        # build all the packages
        run('bin/buildout')
        # Run our migrations
        run('bin/django syncdb --noinput --migrate')

def refresh_app():
    """Restart the app server"""
    sudo('kill -HUP `head -n1 /tmp/dev.oknesset.gunicorn.pid`')
