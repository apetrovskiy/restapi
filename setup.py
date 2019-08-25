# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='restapi',
    version='1.0.0',
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
