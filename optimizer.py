# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 14:46:04 2022

@author: minghuiw
"""

#only focus on Huron now 

import main
import json
import nni

def convert_data(compressed):
    loosedH = {
      "duration_by_phase": {
        "1": {
          "min": 5,
          "priority": 10,
          "release": 5
        },
        "2": {
          "min": 5,
          "priority": 10,
          "release": 5
        },
        "3": {
          "min": 5,
          "priority": 10,
          "release": 5
        },
        "4": {
          "min": 5,
          "priority": 10,
          "release": 5
        }
      },
      "weight_by_phase": {
        "1": 0.45,
        "2": 0.15,
        "3": 0.25,
        "4": 0.15
      }
    }
    
    for phase in range(1,5):
        loosedH['duration_by_phase'][str(phase)]['min'] = compressed['min'+str(phase)+'H']
        loosedH['duration_by_phase'][str(phase)]['priority'] = compressed['priority'+str(phase)+'H']
        loosedH['duration_by_phase'][str(phase)]['release'] = compressed['release'+str(phase)+'H']
        loosedH['weight_by_phase'][str(phase)]= compressed['weight'+str(phase)+'H']
        
    loosedG = {
      "duration_by_phase": {
        "1": {
          "min": 5,
          "priority": 10,
          "release": 5
        },
        "2": {
          "min": 5,
          "priority": 10,
          "release": 5
        },
        "3": {
          "min": 5,
          "priority": 10,
          "release": 5
        },
        "4": {
          "min": 5,
          "priority": 10,
          "release": 5
        }
      },
      "weight_by_phase": {
        "1": 0.45,
        "2": 0.15,
        "3": 0.25,
        "4": 0.15
      }
    }
    
    for phase in range(1,5):
        loosedG['duration_by_phase'][str(phase)]['min'] = compressed['min'+str(phase)+'G']
        loosedG['duration_by_phase'][str(phase)]['priority'] = compressed['priority'+str(phase)+'G']
        loosedG['duration_by_phase'][str(phase)]['release'] = compressed['release'+str(phase)+'G']
        loosedG['weight_by_phase'][str(phase)]= compressed['weight'+str(phase)+'G']
        
    return loosedH, loosedG

def train(params):
    huron_json,green_json = convert_data(params)
    with open("./configs/params/Huron.json", "w") as outfile:
        json.dump(huron_json, outfile)
    with open("./configs/params/Green.json", "w") as outfile:
        json.dump(green_json, outfile)

    main.debug = False
    file = main.main()
    
    f = open(file)
    data = json.load(f)
    
    loss = float(data["Huron"]["total_time_loss"])+float(data["Green"]["total_time_loss"])
    #nni.report_intermediate_result(loss)
    nni.report_final_result(loss)
    
def generate_default_params():
    
    
    return {
    "min1H": 5,
    "priority1H": 10,
    "release1H": 5,
    
    "min2H": 5,
    "priority2H": 10,
    "release2H": 5,
    
    "min3H": 5,
    "priority3H": 10,
    "release3H": 5,
    
    "min4H": 5,
    "priority4H": 10,
    "release4H": 5,
    
    "weight1H": 0.45,
    "weight2H": 0.15,
    "weight3H": 0.25,
    "weight4H": 0.15,

    "min1G": 5,
    "priority1G": 10,
    "release1G": 5,
    
    "min2G": 5,
    "priority2G": 10,
    "release2G": 5,
    
    "min3G": 5,
    "priority3G": 10,
    "release3G": 5,
    
    "min4G": 5,
    "priority4G": 10,
    "release4G": 5,
    
    "weight1G": 0.45,
    "weight2G": 0.15,
    "weight3G": 0.25,
    "weight4G": 0.15
}


try:   
    PARAMS = generate_default_params()
    
    RECEIVED_PARAMS = nni.get_next_parameter()
    #test = {"parameter_id": "3_0_0", "parameter_source": "algorithm", "parameters": {"min1": 8, "min2": 8, "min3": 3, "min4": 6, "priority1": 8, "priority2": 4, "priority3": 8, "priority4": 3, "release1": 3, "release2": 7, "release3": 7, "release4": 5, "weight1": 0.3507279901255561, "weight2": 0.41063724881243446, "weight3": 0.3002143868929728, "weight4": 0.26262657920838317, "TRIAL_BUDGET": 1}}
    #RECEIVED_PARAMS = test['parameters']
    
    PARAMS.update(RECEIVED_PARAMS)
    
    train(PARAMS)

except:
    print("Something else went wrong")