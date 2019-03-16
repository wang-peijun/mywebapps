#!/usr/bin/env python
from glob import glob
import setuptools

setuptools.setup(
      name='MyWebApps',
      version='0.0.1',
      description='web apps',
      author='peijunwang',
      author_email='peijunwang@aliyun.com',
      packages=setuptools.find_packages(),
      py_modules=['manage'],
      include_package_data=True
     )

