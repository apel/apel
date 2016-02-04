"""A setup up script for the APEL."""
from shutil import copyfile
from os import remove
import sys
from setuptools import setup, find_packages


def main():
    """Called when run as script, i.e. "python setup.py install"."""
    if sys.argv[1] == 'install':
        copyfile('bin/client.py', 'bin/apelclient')
        copyfile('bin/parser.py', 'bin/apelparser')
        copyfile('bin/dbloader.py', 'bin/apeldbloader')
        copyfile('bin/dbunloader.py', 'bin/apeldbunloader')
        copyfile('bin/summariser.py', 'bin/apelsummariser')
        copyfile('bin/retrieve_dns.py', 'bin/apelauth')

    conf_dir = '/etc/apel/'
    conf_files = ['conf/client.cfg',
                  'conf/summariser.cfg',
                  'conf/unloader.cfg',
                  'conf/loader.cfg',
                  'conf/db.cfg',
                  'conf/parser.cfg',
                  'conf/auth.cfg']

    data_dir = '/usr/share/apel'
    schema_files = ['schemas/client.sql',
                    'schemas/server.sql',
                    'schemas/server-extra.sql',
                    'schemas/cloud.sql',
                    'schemas/storage.sql']

    accounting_files = ['scripts/slurm_acc.sh', 'htcondor_acc.sh']

    message_files = ['scripts/msg_status.py']

    log_rotate_dir = '/etc/logrotate.d'
    log_rotate_files = ['scripts/apel-client']

    setup(name='apel-ssm',
          version='1.5.1',
          description=("The APEL project provides grid accounting for EGI."),
          author='APEL',
          author_email='apel-admins@stfc.ac.uk',
          download_url='https://github.com/apel/apel/archive/1.5.1-1.zip',
          license='Apache License, v2 - http://www.apache.org/licenses/',
          install_requires=['MySQL-python', 'iso8601', 'python-ldap', 'dirq'],
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
                      (log_rotate_dir, log_rotate_files)])


if sys.argv[1] == 'install':
    remove('bin/apelclient')
    remove('bin/apelparser')
    remove('bin/apeldbloader')
    remove('bin/apeldbunloader')
    remove('bin/apelsummariser')
    remove('bin/apelauth')

if __name__ == "__main__":
    main()
