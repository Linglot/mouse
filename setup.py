from distutils.core import setup

import _config

setup(
    name='Mr Mouse',
    version=_config.CURRENT_VERSION,
    description='A bot for Linglot discord server',
    requires=['discord', 'more_itertools']
)
