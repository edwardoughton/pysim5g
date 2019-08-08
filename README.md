Python SImulator for Modelling 5G (PySIM5G)
===========================================

Description
===========
**PySIM5G** is a software tool, based on the Monte-Carlo simulation method, for simulation modelling of 5G in the sub-6GHz spectrum bands.

The simulator tool allows statistical modelling of different radio interference scenarios for assessing system-level performance of both 4G and 5G spectrum bands.

## Citations:
```
TODO
```

Setup and configuration
=======================

All code for **PySim5G** is written in
Python (Python>=3.5) and has a number of dependencies.
See `requirements.txt` for a full list.

Using conda
-----------

The recommended installation method is to use [conda](http://conda.pydata.org/miniconda.html),
which handles packages and virtual environments,
along with the `conda-forge` channel which has a host of pre-built libraries and packages.

Create a conda environment, using `pyseamcat` as a short reference for digital communications:

    conda create --name pyseamcat python=3.6

Activate it (run each time you switch projects)::

    activate pyseamcat

For development purposes:

Run this command once per machine:

    python setup.py develop

Windows users may need to additionally install `Shapely` as follows:

    conda install shapely

To install pyseamcat permanently:

    python setup.py install

To build the documentation:

    python setup.py docs

Users may need to additionally install `Sphinx` as follows:

    conda install sphinx

And potentially recommonmark:

    pip install recommonmark

The run the tests:

    python setup.py test

To lint for consistent type usage, install `mypy` and run:

    pip install mypy
    mpyp pyseamcat

To lint for general python style, install `pylint` and run:

    pip install pylint
    pylint pyseamcat


Background and funding
======================

The **Python SImulator for Modelling 5G (PySIM5G)** was funded by the the
UK [Digital Catapult's](http://www.digicatapult.org.uk) ESPRC-funded Researcher in Residence
programme.

Contributors
============
- Edward J. Oughton (Oxford)
- Kostas Kotsaros (Digital Catapult)
- Fariborz Entezami (Digital Catapult)
- Dritan Kaleshi (Digital Catapult)
- Catarina Fernandes (Digital Catapult)
- Jon Crowcroft (Cambridge)
