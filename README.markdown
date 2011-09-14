Installation:
=============

For Ubuntu, make sure the following packages are installed:

    sudo apt-get install python python-dev python-imaging python-setuptools

- `python bootstrap.py`

- `bin/buildout`

- `bin/test`

- `bin/django syncdb --migrate`     # do not create a superuser account

- `bin/django loaddata dev`

- `bin/django createsuperuser` # to create your superuser account

- `bin/django runserver`

- `vi src/knesset/local_settings.py` # create your local setting file to store a bunch of things that you do NOT want to push to everyone # NOTE: NEVER push settings.py with local changes!

- sample input for local_settings.py: `DATABASE_NAME = '<your-local-path>dev.db'`  # Or path to database file if using sqlite3.

Trouble?
=======
- Some of the mirrors are flaky so you might need to run the buildout several times until all downloads succeed.
- currently using MySQL as the database engine is not supported
- on bin/buildout, problems with getting distribution for 'PIL' can be fixed 
  by installing the python-dev package

Update - get your branch updated with the changes done by others
======

- cd Open-Knesset 
- git pull git://github.com/hasadna/Open-Knesset.git master
- bin/buildout                     # only needed if the file buildout.cfg was changed; but can't hurt you if you run it every time.
- bin/django syncdb --migrate      # do not create a superuser account
- bin/test
- bin/django runserver

if you get the add_persons_aliases alert try `bin/django migrate --fake persons 0001`

Updating the translation strings:
================================
- cd src/knesset
- ../../bin/django makemessages -a -e txt,html
<edit src/knesset/locale/he/LC_MESSAGES/django.po, find your strings and change it to the correct translation>
- ../../bin/django compilemessages

Windows Users:
--------------

Prerequisites:
- Download and install Python 2.7 from http://www.python.org/download/windows/
- Make sure python and svn are in the system path (control panel->system->advanced->environment variables)
- Download and install svn client from http://www.sliksvn.com/en/download
- Download and install git by following http://help.github.com/win-git-installation/
- Generate an ssh key to your git account by following http://help.github.com/msysgit-key-setup/

Running the installation instructions:
- open command line change dir to the Open-Knesset folder
- run the installation instructions above (Without the $ ofcourse and with backslashes)

Checking in
==============
see http://linux.yyz.us/git-howto.html for a short list of options with git

First time
----------

Every other time
-----------------

- git diff # to know what changed since your last commit
- git add -filename # if you added new files (commit doesn't add new files)
- git commit -a # commit all changes to your local repository
- commit note should include fix#: [number] of the redline bug number youre fixing (if any)
- git push # push changes to git repo
- go to git, do a "pull request" from [release manager] so code will get to production

Updating Text 
==============

Adding a field to existing model
================================

- add the field you want to model sample_model
- see our naming conventions for migrations: under the directory "migrations" under the model's folder - notice the number is added automatically
- so 0003_add_members_blog is actually add_members_blog
- bin/django schemamigration knesset.sample_model --auto naming_convention_change_name
- bin/django syncdb --migrate


 
