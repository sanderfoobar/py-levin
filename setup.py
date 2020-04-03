import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

# Taken from Requests setup.py: https://github.com/psf/requests/blob/master/setup.py#L61
with open(os.path.join(here, 'levin', '__version__.py'), 'r') as f:
    __version__ = None
    exec(f.read())


setup(name='py-levin',
      version=__version__,
      description='Levin client',
      author='xmrdsc',
      url='https://github.com/xmrdsc/py-levin',
      packages=['levin'],
      license='2018 WTFPL – Do What the Fuck You Want to Public License'
     )