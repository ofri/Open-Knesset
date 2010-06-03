from setuptools import setup, find_packages

install_requires = [
    'python-openid',
    'python-yadis',
    'oauth',
    'django-tagging',
    'simplejson',
    'whoosh',
    'django-haystack',
    'South',
    'pyth',
    'django-debug-toolbar',
    'feedparser',
    'pil',
    'django-pagination',
    'django-planet',
    'django-piston',
    'django-extensions',
    ]
setup(
        name = "Open-Knesset",
        version = "0.1",
        url = 'http://github.com/ofri/Open-Knesset',
        license = 'GPLv2',
        description = "Bringing transperancy to the Israeli Knesset",
        author = 'Ofri Raviv and others',
        packages = find_packages('src'),
        package_dir = {'': 'src'},
        install_requires = install_requires,
)


