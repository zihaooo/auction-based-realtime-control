# -*- coding: utf-8 -*-

import os

try:
    if os.name == 'posix':
        import libsumo as traci
        print('libsumo imported!')
    else:
        import traci
        print('traci imported!')
except ImportError:
    import traci
