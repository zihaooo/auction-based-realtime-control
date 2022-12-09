# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 16:03:33 2022

@author: minghuiw
"""
from pathlib import Path

from nni.experiment import Experiment

min_green = 7

search_space = {
    "min1H": {"_type": "randint", "_value": [min_green, 20]},
    "priority1H": {"_type": "randint", "_value": [10, 25]},
    "release1H": {"_type": "randint", "_value": [10, 20]},

    "min2H": {"_type": "randint", "_value": [0, 10]},
    "priority2H": {"_type": "randint", "_value": [2, 10]},
    "release2H": {"_type": "randint", "_value": [2, 10]},

    "min3H": {"_type": "randint", "_value": [min_green, 10]},
    "priority3H": {"_type": "randint", "_value": [0, 10]},
    "release3H": {"_type": "randint", "_value": [0, 10]},

    "min4H": {"_type": "randint", "_value": [0, 15]},
    "priority4H": {"_type": "randint", "_value": [2, 15]},
    "release4H": {"_type": "randint", "_value": [2, 15]},

    "weight1H": {"_type": "uniform", "_value": [0.1, 1]},
    "weight2H": {"_type": "uniform", "_value": [0.1, 1]},
    "weight3H": {"_type": "uniform", "_value": [0.1, 1]},
    "weight4H": {"_type": "uniform", "_value": [0.1, 1]},

    "min1G": {"_type": "randint", "_value": [min_green, 20]},
    "priority1G": {"_type": "randint", "_value": [10, 25]},
    "release1G": {"_type": "randint", "_value": [10, 20]},

    "min2G": {"_type": "randint", "_value": [0, 10]},
    "priority2G": {"_type": "randint", "_value": [0, 10]},
    "release2G": {"_type": "randint", "_value": [0, 10]},

    "min3G": {"_type": "randint", "_value": [min_green, 10]},
    "priority3G": {"_type": "randint", "_value": [2, 15]},
    "release3G": {"_type": "randint", "_value": [2, 15]},

    "min4G": {"_type": "randint", "_value": [0, 10]},
    "priority4G": {"_type": "randint", "_value": [5, 15]},
    "release4G": {"_type": "randint", "_value": [0, 10]},

    "weight1G": {"_type": "uniform", "_value": [0.1, 1]},
    "weight2G": {"_type": "uniform", "_value": [0.1, 1]},
    "weight3G": {"_type": "uniform", "_value": [0.1, 1]},
    "weight4G": {"_type": "uniform", "_value": [0.1, 1]},
}

experiment = Experiment('local')

experiment.config.trial_command = 'python optimizer.py'
experiment.config.trial_code_directory = '.'
experiment.config.search_space = search_space
experiment.config.tuner.name = 'GP'

experiment.config.tuner.class_args = {
    'optimize_mode': 'minimize',
    'utility': 'ei',
    'kappa': 5.0,
    'xi': 0.0,
    'nu': 2.5,
    'alpha': 1e-6,
    'cold_start_num': 20,
    'selection_num_warm_up': 20,
    'selection_num_starting_points': 20
}
experiment.config.max_trial_number = 500
experiment.config.trial_concurrency = 1
experiment.config.max_trial_duration = '30s'

# experiment.run(9090)
# experiment.resume('yhvn2kr9', 9090)
