# Installation #

## Get the code ##
- Make sure you have git installed, and have an account on github.com. Sign into github. see http://linux.yyz.us/git-howto.html for a short list of options with git and github.com help for more.
- Fork the repository (https://github.com/hasadna/Open-Knesset, top right of page). This creates a copy of the repository under your user.
- Clone the repository: `git clone https://github.com/your-username/Open-Knesset.git` . This creates a copy of the project on your local machine.
If you haven't done so already:
- `git config --local user.name "Your Name"`
- `git config --local user.email "your@email.com"`

## Prerequisites ##
- Python 2.x (including dev files)
- python-setuptools

In Ubuntu this can be done with:

    sudo apt-get install python python-dev python-setuptools python-lxml

## Installation process ##
- `python bootstrap.py`
- `bin/buildout` (if you have a problem, see "Trouble?" below)
- `bin/test`
- `bin/django syncdb --migrate`     # do not create a superuser account
- `bin/django loaddata dev`
- `bin/django createsuperuser` # to create your superuser account
- `bin/django runserver`
- `vi src/knesset/local_settings.py` # create your local setting file to store a bunch of things that you do NOT want to push to everyone # NOTE: NEVER push settings.py with local changes!
- sample input for local_settings.py: `DATABASE_NAME = '<your-local-path>dev.db'`  # Or path to database file if using sqlite3.

Note: at this point the bills view is missing bills names. To fix this you can run the time intensive:
- bin/django shell_plus
- for bill in Bill.objects.all(): bill.save()
or run this for just several bills:
- for bill in Bill.objects.all()[:100]: bill.save()

## Trouble? ##
- Some of the mirrors are flaky so you might need to run the buildout several times until all downloads succeed.
- currently using MySQL as the database engine is not supported
- on bin/buildout, problems with getting distribution for 'PIL' can be fixed
  by installing the python-dev package

## Windows Users ##
Prerequisites:
- Download and install Python 2.7 from http://www.python.org/download/windows/
- Download and install git by following http://help.github.com/win-git-installation/
- Generate an ssh key to your git account by following http://help.github.com/msysgit-key-setup/

Running the installation instructions:
- open command line change dir to the Open-Knesset folder
- run the installation instructions above (Without the $ ofcourse and with backslashes)

# Working process #

## Before you code ##
Get your branch updated with the changes done by others. Please do this every time before you start developing:

- `cd Open-Knesset`
- `git pull git@github.com:hasadna/Open-Knesset.git master`
- `bin/buildout`                     # only needed if the file buildout.cfg was changed; but can't hurt you if you run it every time.
- `bin/django syncdb --migrate`      # do not create a superuser account
- `bin/test`                         # if there are any failures, contact the other developers to see if that's something you should worry about.
- `bin/django runserver`             # now you can play with the site using your browser

if you get the add_persons_aliases alert try `bin/django migrate --fake persons 0001`

## When you code ##
### General ###
- Write tests for everything that you write.
- Keep performance in mind - test the number of db queries your code performs using `bin/django runserver` and access a page that runs the code you changed. See the output of the dev-server before and after your change.

### Adding a field to existing model ###
We use south to manage database migration. The work process looks something like:
- add the field you want to model sample_model in app sample_app
- bin/django schemamigration sample_app --auto # this generates a new migration under src/knesset/sample_app/migrations. You should review it to make sure it does what you expect.
- bin/django syncdb --migrate # run the migration.
- don't forget to git add/commit the migration file.

### Updating the translation strings ###
Currently, there is no need to update translation (po) files. Its a real headache to merge when there are conflicts, so simply add a note to the commit message "need translations" if you added any _('...') or {% trans '...' %} to the code.

## After you code ##
- `bin/test` # make sure you didn't break anything
- `git status` # to see what changes you made
- `git diff filename` # to see what changed in a specific file
- `git add filename` # for each file you changed/added.
- `git commit -m` "commit message" # Please write a sensible commit message, and include "fix#: [number]" of the issue number you're working on (if any).
- `git push` # push changes to git repo
- go to github.com and send a "pull request" so your code will be reviewed and pulled into the main branch, make sure the base repo is *hasadna/Open-Knesset*.
