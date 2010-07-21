# stolen from Jannis Leidel
# http://bitbucket.org/jezdez/django-authority/src/tip/setup.py
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='weewar-monitor',
    version='0.1b1',
    description='A small GTK application watches you Weewar games for you.',
    long_description=read('README'),
    maintainer='Sebastian Rahlf',
    maintainer_email='basti AT redtoad DOT de',
    license='GPLv3',
    url='http://bitbucket.org/basti/weewar-monitor/',
    download_url='http://bitbucket.org/basti/weewar-monitor/downloads/',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Games/Entertainment :: Turn Based Strategy',
        'Environment :: X11 Applications :: GTK', 
        'Topic :: System :: Monitoring',
    ],
    zip_safe=False,
    scripts = ['src/weewar-monitor'],
)

