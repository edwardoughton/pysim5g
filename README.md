python simulator for integrated modelling of 5G (pysim5g)
===========================================

[![Build Status](https://travis-ci.com/edwardoughton/pysim5g.svg?branch=master)](https://travis-ci.com/edwardoughton/pysim5g)
[![Coverage Status](https://coveralls.io/repos/github/edwardoughton/pysim5g/badge.svg?branch=master)](https://coveralls.io/github/edwardoughton/pysim5g?branch=master)

Description
===========
**pysim5g** is an open-source software tool, based on the Monte-Carlo method, for integrated engineering-economic modeling of 5G.

Statistical analysis of radio interference enables system-level performance to be assessed for designated 4G and 5G frequency bands (including millimeter wave), providing quantified analytics on (i) the economics of ultra-dense 5G networks, (ii) 5G spectral efficiency gains and (iii) the capacity and coverage of 4G/5G coexistence.

One example application of this framework includes exploring the techno-economics of 5G infrastructure sharing strategies.

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

    conda create --name pysim5g python=3.5

Activate it (run each time you switch projects)::

    activate pysim5g

First, install required packages including `fiona`, `shapely`, `numpy`, `rtree`, `pyproj` and `pytest`:

    conda install fiona shapely numpy rtree pyproj pytest

For development purposes, run this command once per machine:

    python setup.py develop

To install pysim5g permanently:

    python setup.py install

To build the documentation:

    python setup.py docs

The run the tests:

    pytest

To visualize the results, install `matplotlib`, `pandas` and `seaborn`:

    conda install matplotlib pandas seaborn

And then run:

    python vis/vis.py

Background and funding
======================

The **python simulator for integrated modelling of 5G (pysim5g)** was funded by the
UK [Digital Catapult's](http://www.digicatapult.org.uk) ESPRC-funded Researcher in Residence
programme.

Contributors
============
- Edward J. Oughton (University of Oxford) (Primary Investigator)
- Kostas Kotsaros (UK Digital Catapult)
- Fariborz Entezami (UK Digital Catapult)
- Dritan Kaleshi (UK Digital Catapult)
- Catarina Fernandes (UK Digital Catapult)
- Tom Russell (University of Oxford)
- Jon Crowcroft (University of Cambridge)
