# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 16:03:33 2022

@author: minghuiw
"""

from nni.experiment import Experiment

search_space = {
    "min1H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority1H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release1H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "min2H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority2H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release2H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "min3H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority3H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release3H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "min4H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority4H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release4H": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "weight1H": {"_type":"uniform","_value":[0.1,0.5]},
    "weight2H": {"_type":"uniform","_value":[0.1,0.5]},
    "weight3H": {"_type":"uniform","_value":[0.1,0.5]},
    "weight4H": {"_type":"uniform","_value":[0.1,0.5]},
    
    "min1G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority1G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release1G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "min2G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority2G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release2G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "min3G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority3G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release3G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "min4G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "priority4G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    "release4G": {"_type": "choice", "_value": [3,4,5,6,7,8,9,10]},
    
    "weight1G": {"_type":"uniform","_value":[0.1,0.5]},
    "weight2G": {"_type":"uniform","_value":[0.1,0.5]},
    "weight3G": {"_type":"uniform","_value":[0.1,0.5]},
    "weight4G": {"_type":"uniform","_value":[0.1,0.5]}
}


experiment = Experiment('local')

experiment.config.trial_command = 'python optimizer.py'
experiment.config.trial_code_directory = 'E:\Project'
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
experiment.config.max_trial_number = 500
experiment.config.trial_concurrency = 1

experiment.run(8080)


