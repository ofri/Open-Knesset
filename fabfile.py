'''
Open-Knesset fabfile. Usage:

$ fab [staging|production] setup deploy # for the first time
$ fab [staging|production] deploy # to run the latest version
'''
# Default release is 'current'
config.release = 'current'
config.repository = 'git://github.com/ofri/Open-Knesset.git'

def staging():
    """Staging server settings"""
    config.settings = 'tuzig_staging'
    config.path = '/home/daonb/sites/staging.Open-Knesset'
    config.fab_hosts = ['staging.tzafim.org']
    config.fab_user = 'daonb'

def production():
    """Production server settings"""
    config.settings = 'tuzig'
    config.path = '/home/daonb/sites/Open-Knesset'
    config.fab_hosts = ['tzafim.org']
    config.fab_user = 'daonb'

def setup():
    """
    Setup a fresh env and install everything we need so it's ready to deploy to
    """
    run('mkdir -p $(path); mkdir $(path)/releases')
    clone_repo()
    checkout_latest()

def deploy():
    """Deploy the latest version of the site to the server and restart apache"""
    checkout_latest()
    symlink_current_release()
    migrate()
    restart_web_server()

def clone_repo():
    """Do initial clone of the git repo"""
    run('cd $(path); git clone $(repository) repository')

def checkout_latest():
    """Pull the latest code into the git repo and copy to a timestamped release directory"""
    import time
    config.release = time.strftime('%Y%m%d%H%M%S')
    run('cd $(path)/repository; git pull;')
    install_env()
    run('cp -R $(path)/repository $(path)/releases/$(release)')
    run('rm -rf $(path)/releases/$(release)/.git*')

def install_env():
    """Install the required packages using pip"""
    run('cd $(path)/repository; python bootstrap.py; bin/buildout')

def symlink_current_release():
    """Symlink our current release, uploads and settings file"""
    run('cd $(path); rm project; ln -s releases/current project; rm releases/current; ln -s $(release) releases/current')
    run('cd $(path)/releases/current/src/knesset; ln -s settings_$(settings).py runsettings.py', fail='ignore')

def migrate():
    """Run our migrations"""
    run('cd $(path)/releases/current; bin/django syncdb --noinput')
    # for south: run('cd $(path)/releases/current; bin/django syncdb --noinput --migrate')

def restart_web_server():
    """Restart the web server"""
    sudo('apache2ctl restart')
