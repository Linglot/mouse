from distutils.core import setup

from settings import config

setup(
    name='Mr Mouse',
    version=config.CURRENT_VERSION,
    description='A bot for Linglot discord server',
    requires=['discord', 'more_itertools']
)
