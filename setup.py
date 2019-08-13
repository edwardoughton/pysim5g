#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Setup package
"""
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages
from setuptools import setup


def readme():
    """Read README contents
    """
    with open('README.md') as f:
        return f.read()


setup(
    name='pysim5g',
    use_scm_version=True,
    license='MIT License',
    description='5G simulator',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author='Ed Oughton',
    author_email='edward.oughton@ouce.ox.ac.uk',
    url='https://github.com/edwardoughton/pysim5g',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    setup_requires=[
        'setuptools_scm'
    ],
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
        'fiona>=1.7.13',
        'shapely>=1.6',
        'numpy',
        'rtree>=0.8',
        'pyproj>=2',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            # eg: 'snkit = snkit.cli:main',
        ]
    },
)
