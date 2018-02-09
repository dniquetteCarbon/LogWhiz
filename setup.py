from setuptools import setup, find_packages

setup(
    name='cbd-support',
    description='Python tool set for Defense Sensor and Backend(server).',
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-jsonpify',
        'flask-restful'
    ],
    include_package_data=True)
