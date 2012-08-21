from fabric.api import run, env,cd, sudo, roles

# add a local_fab_settings.py file,
# so that you can access your servers
# but please, don't commit it to git.
try: 
    from local_fab_settings import *
except ImportError as e:
    pass

# web server stuff
def apache_cmd(cmd):
	if cmd not in ['start','stop','restart']:
		raise Exception('Unknown apache command %s' % cmd)
	sudo('/etc/init.d/apache2 %s' % cmd)

def update_commit():
	with cd("/oknesset_web/Open-Knesset"):
		sudo('git log --pretty=format:"Code Commit: %H <br>Last Update: %cd" -n 1 > src/knesset/templates/last_build.txt',
			user='oknesset')

def chown(to_user,directory='Open-Knesset'):
	sudo("chown -R %s %s" % (to_user,directory))

@roles('web')
def deploy_web(with_buildout=False):
	apache_cmd('stop')
	with cd('/oknesset_web'):
		chown('oknesset')
		with cd('Open-Knesset'):
			git_pull()
			if with_buildout:
				buildout()
			update_commit()
		chown('www-data')
	apache_cmd('start')

# db server stuff - should only run once on master db!
def migrate_syncdb():
	with cd("/oknesset_data/Open-Knesset"):
		run("bin/django syncdb --migrate")

@roles('db')
def deploy_backend(with_migration=False,with_buildout=False):
	with cd("/oknesset_data/Open-Knesset"):
		git_pull()
		if with_buildout:
			buildout()
		if with_migration:
			migrate_syncdb()

@roles('db')
def check_replication():
	# works on both servers
	run('ps -ef | grep postgres | grep -e receiver -e sender')

# memcache commands
@roles('memcache')
def memcache_flushall():
	run('echo flush_all | telnet localhost 11211')

# commands for all servers
def git_pull(repo='origin', branch='master',as_user='oknesset'):
	sudo("git pull %s %s" % (repo,branch),user=as_user)

def buildout():
	sudo('bin/buildout',user='oknesset')

def system_upgrade():
	sudo('apt-get update')
	sudo('apt-get upgrade')

def deploy_all(repo='origin', branch='master',with_buildout=False,with_migration=False,reset_memcache=False):
    deploy_backend(with_buildout=with_buildout,with_migration=with_migration)
    deploy_web(with_buildout=with_buildout)
    if reset_memcache:
    	memcache_flushall()

def host_cmd(cmd):
	run(cmd)