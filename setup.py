#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="pysectools",
    version="0.5.2",
    description="""A package of security-related Python functions. Dropping
    privileges, entering sandboxes, generating random numbers, asking for
    passwords...""",
#    long_description="""""",
    license="Unlicense",
    author="Greg V",
    author_email="greg@unrelenting.technology",
    url="https://github.com/myfreeweb/pysectools",
    packages=["pysectools"],
    keywords=["security", "pinentry", "getpass", "capsicum", "random", "rng",
              "arc4random"],
    classifiers=[
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: Public Domain",
        "Topic :: Security"
    ],
    include_package_data=True,
    zip_safe=False,
    package_data={
        "": ["README.md", "COPYING"]
    }
)
