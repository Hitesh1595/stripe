# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in stripe/__init__.py
from stripe import __version__ as version

setup(
	name='stripe',
	version=version,
	description='stripe',
	author='stripe',
	author_email='hit@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
