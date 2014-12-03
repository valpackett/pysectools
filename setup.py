#!/usr/bin/env python
#import sys
from distutils.core import setup

# if sys.version < '2.5':
#     sys.exit('Python 2.5 or higher is required')

setup(name='pysectools',
      version='0.3.0',
      description="""A package of security-related Python functions. Dropping
      privileges, entering sandboxes, generating random numbers, asking for
      passwords...""",
#      long_description="""""",
      license='WTFPL',
      author='Greg V',
      author_email='greg@unrelenting.technology',
      url='https://github.com/myfreeweb/pysectools',
      packages=['pysectools'],
      keywords=['security', 'pinentry', 'getpass', 'capsicum', 'random', 'rng',
                'arc4random'],
      classifiers=[
          'Operating System :: POSIX',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'License :: Public Domain',
          'Topic :: Security'
      ],
      package_data={})
