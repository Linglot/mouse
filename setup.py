from distutils.core import setup

from settings.constants import CURRENT_VERSION

setup(
    name='Mr Mouse',
    version=CURRENT_VERSION,
    description='A bot for Linglot discord server',
    requires=['discord', 'more_itertools']
)
