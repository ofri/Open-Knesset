from fabric.api import run, env,cd, sudo

env.user = 'oknesset'

def deploy(repo='origin', branch='master'):
    with cd("live"):
        run("git pull %s %s" % (repo, branch))
    sudo ('restart oknesset')
