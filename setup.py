# -*- coding: utf-8 -*-
__author__ = 'wgz'

from setuptools import setup, find_packages

setup(
  name="dou",
  version="0.10",
  description="My test module",
  author="Douglas",
  url="http://www.github.com",
  license="LGPL",
  packages=find_packages(),
  # scripts=["scripts/test.py"],
  platforms='any',
  # py_modules=['ez_setup'],
  package_dir={'': '.'},
  package_data={'': ['*.bat', '*.cfg'], },
  include_package_data=True,

  install_requires=[],
  keywords="Douglas toolset"

)
