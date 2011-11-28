
from setuptools import setup, find_packages

install_requires = [
    'python-openid',
    'python-dateutil',
#    'python-yadis',
    'oauth',
    'django-tagging',
    'South',
    'pyth',
    'django-debug-toolbar',
    'feedparser',
    'pil',
    'django-pagination',
    # 'django-piston',
    'django-extensions',
    'python-memcached',
    'BeautifulSoup',
    'nose',
    'django-nose',
    'gunicorn'
    ]
setup(
        name = "Open-Knesset",
        version = "0.1",
        url = 'http://github.com/ofri/Open-Knesset',
        description = "Bringing transperancy to the Israeli Knesset",
        author = 'Ofri Raviv and others',
        packages = find_packages('src'),
        package_dir = {'': 'src'},
        install_requires = install_requires,
        classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: Hebrew',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: JavaScript'],
)


