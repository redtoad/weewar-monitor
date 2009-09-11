# stolen from Jannis Leidel
# http://bitbucket.org/jezdez/django-authority/src/tip/setup.py
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='python-weewar-monitor',
    version='0.1',
    description="A Django app that provides generic per-object-permissions for Django's auth app.",
    long_description=read('README'),
    maintainer='Sebastian Rahlf',
    maintainer_email='basti AT redtoad DOT de',
    license='GPLv3',
    url='http://bitbucket.org/basti/python-weewar-monitor/',
    download_url='http://bitbucket.org/basti/python-weewar-monitor/downloads/',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)

