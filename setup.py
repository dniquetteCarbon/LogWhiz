from setuptools import setup, find_packages

setup(
    name='logwhiz',
    description='Python tool for working with Defense log',
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-jsonpify',
        'flask-restful'
    ],
    include_package_data=True)
