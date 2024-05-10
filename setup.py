# -*- coding: utf-8 -*-

# Learn more: https://github.com/maikovisky/sliceisolation

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sliceisolation',
    version='0.1.0',
    description='Slice Isolation package for Master Experiments',
    long_description=readme,
    author='Maiko de Andrade',
    author_email='maikovisky@gmail.com',
    url='https://github.com/maikovisky/sliceisolation',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'samples'))
)