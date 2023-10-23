from setuptools import setup
from setuptools import find_packages

setup(
    name='lueftungstool',
    version='0.1-dev',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'Flask >=2, <3',
        'flask-openapi3',
        'scipy',
    ],
)
