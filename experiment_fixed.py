# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 16:03:33 2022

@author: minghuiw
"""

from nni.experiment import Experiment

search_space = {
    "1H": {"_type": "randint", "_value": [20,65]},
    "2H": {"_type": "randint", "_value": [3,25]},
    "3H": {"_type": "randint", "_value": [3,25]},
    "4H": {"_type": "randint", "_value": [0,30]},
    
    "1G": {"_type": "randint", "_value": [20,65]},
    "2G": {"_type": "randint", "_value": [3,25]},
    "3G": {"_type": "randint", "_value": [3,25]},
    "4G": {"_type": "randint", "_value": [0,30]},
}

experiment = Experiment('local')

experiment.config.trial_command = 'python optimizer_fixed.py'
experiment.config.trial_code_directory = 'F:\courses\CEE551\Project'
experiment.config.search_space = search_space
experiment.config.tuner.name = 'GP'

experiment.config.tuner.class_args = {
    'optimize_mode': 'minimize',
    'utility': 'poi',
    'kappa': 5.0,
    'xi': 0.0,
    'nu': 2.5,
    'alpha': 1e-6,
    'cold_start_num': 20,
    'selection_num_warm_up': 100000,
    'selection_num_starting_points': 250
}
experiment.config.max_trial_number = 20
experiment.config.trial_concurrency = 1

experiment.run(8080)
