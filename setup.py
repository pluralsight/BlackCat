from distutils.core import setup

from setuptools import find_packages


# def find(cls, where='.', exclude=(), include=('*',)):
setup(name='blackcat',
      version='1.0.4',
      description='Centralized reporting on GitHub dependency scanning outputs',
      author='Dylan Katz',
      author_email='dylan-katz@-pluralsight.com',
      packages=find_packages(include=["blackcat.*", "blackcat"], exclude=["blackcat.test.*"]))
