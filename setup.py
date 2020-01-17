from distutils.core import setup

setup(name='blackcat',
      version='1.0.4a',
      description='Centralized reporting on GitHub dependency scanning outputs',
      author='Dylan Katz',
      author_email='dylan-katz@-pluralsight.com',
      packages=['blackcat', 'blackcat.postprocessing'])