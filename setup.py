# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='restapi',
    version='0.1.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'pymongo',
        'fastjsonschema',
        'pytest',
        'coverage',
        'numpy',
        'gunicorn'
    ]
)
