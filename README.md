python simulator for modelling 5G (pysim5g)
===========================================

Description
===========
**pysim5g** is a software tool, based on the Monte-Carlo simulation method, for simulation modelling of 5G in the sub-6GHz spectrum bands.

The simulator tool allows statistical modelling of different radio interference scenarios for assessing system-level performance of both 4G and 5G spectrum bands.

## Citations:
```
TODO
```

Setup and configuration
=======================

All code for **pysim5g** is written in
Python (Python>=3.5) and has a number of dependencies.
See `requirements.txt` for a full list.

Using conda
-----------

The recommended installation method is to use [conda](http://conda.pydata.org/miniconda.html),
which handles packages and virtual environments,
along with the `conda-forge` channel which has a host of pre-built libraries and packages.

Create a conda environment called `pysim5g`:

    conda create --name pysim5g python=3.6

Activate it (run each time you switch projects)::

    activate pysim5g

First, install required packages including `Fiona`, `shapely`, `numpy`, `rtree` and `pyproj`:

    conda install fiona shapely numpy rtree pyproj

For development purposes, run this command once per machine:

    python setup.py develop

To install pysim5g permanently:

    python setup.py install

To build the documentation:

    python setup.py docs

The run the tests:

    python setup.py test

Background and funding
======================

The **Python SImulator for Modelling 5G (PySIM5G)** was funded by the
UK [Digital Catapult's](http://www.digicatapult.org.uk) ESPRC-funded Researcher in Residence
programme.

Contributors
============
- Edward J. Oughton (Oxford)
- Kostas Kotsaros (Digital Catapult)
- Fariborz Entezami (Digital Catapult)
- Dritan Kaleshi (Digital Catapult)
- Catarina Fernandes (Digital Catapult)
- Tom Russell (Oxford)
- Jon Crowcroft (Cambridge)
