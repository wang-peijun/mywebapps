#!/usr/bin/env python
from glob import glob
from distutils.core import setup
import setuptools

setuptools.setup(
      name='mywebapps',
      version='0.0.1',
      description='A personal web apps site',
      author='peijunw',
      author_email='',
      url='',
      packages=['polls', 'mywebapp', 'myauth', 'polls.migrations', 'myauth.migrations'],
      py_modules=['manage'],
      data_files=glob('templates/**/*', recursive=True) + glob('static/**/*', recursive=True) + ['requirements'] +
                 glob('polls/**/*', recursive=True) + glob('myauth/**/*', recursive=True)
     )

