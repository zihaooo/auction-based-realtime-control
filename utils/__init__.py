# -*- coding: utf-8 -*-

import os

try:
    if os.name == 'posix':
        import libsumo as traci
    else:
        import traci
except ImportError:
    import traci
