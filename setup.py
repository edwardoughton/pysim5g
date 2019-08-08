#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for PySIM5G.

    This file was generated with PyScaffold 2.5.7, a tool that easily
    puts up a scaffold for your new Python project. Learn more under:
    http://pyscaffold.readthedocs.org/

"""
import os
import shutil
import sys
import getpass
import re
import zipfile
from datetime import date
from setuptools import setup


def setup_package():
    needs_sphinx = {'build_sphinx', 'upload_docs'}.intersection(sys.argv)
    sphinx = ['sphinx'] if needs_sphinx else []
    setup(setup_requires=['six', 'pyscaffold>=3.0a0,<3.1a0'] + sphinx,
          use_pyscaffold=True)


def get_raw_data():
    import pysftp

    print('')
    reply = str(input('Would you like to download the raw data from the smif ftp server? (y/n): ')).lower().strip()

    if reply[:1] != 'y':
        exit()

    folder = os.path.join('data', 'raw')

    # Clear raw data directory
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    # Download file from server
    user = input("Username:")
    passwd = getpass.getpass("Password for " + user + ":")

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection('ceg-itrc.ncl.ac.uk', username=user, password=passwd, cnopts=cnopts) as sftp:
        with sftp.cd('data/digital_communications'):

            # Get list of files, sort by date, ask user to choose a file and download to data/raw
            ftp_files = sftp.listdir()

            datafiles = []
            for datafile in ftp_files:
                m = re.search("([0-9]{4})\_([0-9]{2})\_([0-9]{2})", datafile)
                datafiles.append(
                    (datafile, date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
                )

            datafiles = sorted(datafiles, key=lambda datafile: datafile[1])

            print('')
            print('Available datafiles:')
            for idx, datafile in enumerate(datafiles):
                print(str(idx) + ': ' + datafile[0])

            reply = str(input('Choose a file by number, or press enter to download latest: ')).lower().strip()

            if (reply == ''):
                reply = len(datafile)

            print('Downloading ' + datafiles[int(reply)][0] + ' ...')
            sftp.get(datafiles[int(reply)][0], localpath=os.path.join(folder, 'raw.zip'))

    # Unzip the file
    print('Extracting files ...')
    zip_ref = zipfile.ZipFile(os.path.join(folder, 'raw.zip'), 'r')
    zip_ref.extractall(folder)
    zip_ref.close()
    print('Done')


if __name__ == "__main__":
    if 'get_raw_data' in sys.argv:
        get_raw_data()
    else:
        setup_package()
