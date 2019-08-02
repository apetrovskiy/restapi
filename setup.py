# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='restapi',
    version='0.1.5',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'pymongo',
        'jsonschema',
        'pytest',
        'coverage',
        'numpy',
        'gunicorn'
    ]
)
