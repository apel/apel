"""A setup script for APEL.

This script installs the APEL library, client, parsers and server. This
should be similar to installing the RPMs for apel-lib, apel-client,
apel-parsers, and apel-server, although there may be some differences.
A known difference is the RPM installs pyc and pyo files,
whereas this script does not.

Usage: 'python setup.py install'

Requires setuptools.
"""

import glob
from os import remove
from shutil import copyfile
import sys

from setuptools import setup, find_packages

from apel import __version__


def setup_temp_files():
    """Create temporary files with deployment names. """
    copyfile('bin/client.py', 'bin/apelclient')
    copyfile('bin/parser.py', 'bin/apelparser')
    copyfile('bin/dbloader.py', 'bin/apeldbloader')
    copyfile('bin/dbunloader.py', 'bin/apeldbunloader')
    copyfile('bin/summariser.py', 'bin/apelsummariser')
    copyfile('bin/retrieve_dns.py', 'bin/apelauth')


def main():
    """Called when run as script, e.g. 'python setup.py install'."""
    supported_commands = {
        "install",
        "build",
        "bdist",
        "develop",
        "build_scripts",
        "install_scripts",
        "install_data",
        "bdist_dumb",
        "bdist_egg",
    }

    if supported_commands.intersection(sys.argv):
        setup_temp_files()

    # conf_files will later be copied to conf_dir
    conf_dir = '/etc/apel/'
    conf_files = ['conf/client.cfg',
                  'conf/summariser.cfg',
                  'conf/unloader.cfg',
                  'conf/loader.cfg',
                  'conf/db.cfg',
                  'conf/parser.cfg',
                  'conf/auth.cfg']

    # schema_files, update_scripts, accounting_files,
    # and message_files will later be copied to data_dir
    data_dir = '/usr/share/apel'
    schema_files = ['schemas/client.sql',
                    'schemas/server.sql',
                    'schemas/server-extra.sql',
                    'schemas/cloud.sql',
                    'schemas/storage.sql']

    # Wildcarding for update scripts (like we do in the spec file)
    # prevents having to manually update this variable.
    update_scripts = glob.glob('scripts/update-*.sql')

    accounting_files = ['scripts/slurm_acc.sh', 'scripts/htcondor_acc.sh']

    message_files = ['scripts/msg_status.py']

    # log_rotate_files will later be copied to log_rotate_dir
    log_rotate_dir = '/etc/logrotate.d'
    log_rotate_files = ['scripts/apel-client']

    # Python 3.x dependencies
    _install_requires = ['mysqlclient', 'iso8601', 'python-ldap', 'dirq', 'future']
    # Python 2.x dependencies
    if sys.version_info < (3,):
        _install_requires = ['MySQL-python'] + _install_requires[1:]

    # For 'python setup.py install' to
    # work (on Linux SL6), 'python-daemon'
    # must be installed or included
    # in install_required
    setup(name='apel',
          version='%i.%i.%i' % __version__,
          description=("The APEL project provides grid accounting for EGI."),
          author='APEL',
          author_email='apel-admins@stfc.ac.uk',
          url='http://apel.github.io/',
          download_url='https://github.com/apel/apel/releases',
          license='Apache License, Version 2.0',
          install_requires=_install_requires,
          extras_require={
              'python-daemon': ['python-daemon'],
          },
          packages=find_packages(exclude=['bin']),
          scripts=['bin/apelclient',
                   'bin/apelparser',
                   'bin/apeldbloader',
                   'bin/apeldbunloader',
                   'bin/apelsummariser',
                   'bin/apelauth'],
          data_files=[(conf_dir, conf_files),
                      (data_dir, schema_files),
                      (data_dir, accounting_files),
                      (data_dir, message_files),
                      (data_dir, update_scripts),
                      (log_rotate_dir, log_rotate_files),
                      # Create empty directories
                      ('/var/log/apel', []),
                      ('/var/run/apel', []),
                      ],
          # zip_safe allows setuptools to install the project
          # as a zipfile, for maximum performance!
          # We have disabled this feature so installing via the setup
          # script is similar to installing the RPM apel-ssm
          zip_safe=False)

    # Remove temporary files with deployment names
    if supported_commands.intersection(sys.argv):
        remove('bin/apelclient')
        remove('bin/apelparser')
        remove('bin/apeldbloader')
        remove('bin/apeldbunloader')
        remove('bin/apelsummariser')
        remove('bin/apelauth')


if __name__ == "__main__":
    main()
