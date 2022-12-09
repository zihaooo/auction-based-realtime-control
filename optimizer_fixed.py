# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 14:46:04 2022

@author: minghuiw
"""
import traceback

import test_fixed
import json
import nni

min_green = 7
greenH = 96
greenG = 95


def convert_data(compressed):
    # For Huron
    loosedH = {
        "effective_green": greenH,
        "green_by_phase": {
            "1": 52,
            "2": 14,
            "3": 13,
            "4": 17
        }
    }

    sum_green = 0
    for phase in range(1, 5):
        sum_green += compressed[str(phase) + 'H']

    loosedH['green_by_phase']['1'] = int(compressed['1H'] / sum_green * (greenH - 2 * min_green)) + min_green
    loosedH['green_by_phase']['2'] = int(compressed['2H'] / sum_green * (greenH - 2 * min_green))
    loosedH['green_by_phase']['3'] = int(compressed['3H'] / sum_green * (greenH - 2 * min_green)) + min_green
    loosedH['green_by_phase']['4'] = greenH - loosedH['green_by_phase']['1'] - loosedH['green_by_phase']['2'] - \
                                     loosedH['green_by_phase']['3']

    # For Green
    loosedG = {
        "effective_green": greenG,
        "green_by_phase": {
            "1": 52,
            "2": 14,
            "3": 13,
            "4": 17
        }
    }

    sum_green = 0
    for phase in range(1, 5):
        sum_green += compressed[str(phase) + 'G']

    loosedG['green_by_phase']['1'] = int(compressed['1G'] / sum_green * (greenG - 2 * min_green)) + min_green
    loosedG['green_by_phase']['2'] = int(compressed['2G'] / sum_green * (greenG - 2 * min_green))
    loosedG['green_by_phase']['3'] = int(compressed['3G'] / sum_green * (greenG - 2 * min_green)) + min_green
    loosedG['green_by_phase']['4'] = greenG - loosedG['green_by_phase']['1'] - loosedG['green_by_phase']['2'] - \
                                     loosedG['green_by_phase']['3']

    return loosedH, loosedG


def train(params):
    huron_json, green_json = convert_data(params)
    with open("./configs/plans/Huron.json", "w") as outfile:
        json.dump(huron_json, outfile, indent=2)
    with open("./configs/plans/Green.json", "w") as outfile:
        json.dump(green_json, outfile, indent=2)

    test_fixed.debug = False
    data = test_fixed.main()

    loss = float(data["Huron"]["total_time_loss"]) + float(data["Green"]["total_time_loss"])
    # nni.report_intermediate_result(loss)
    nni.report_final_result(loss)


def generate_default_params():
    return {
        "1H": 52 - min_green,
        "2H": 14,
        "3H": 13 - min_green,
        "4H": 17,

        "1G": 56 - min_green,
        "2G": 7,
        "3G": 16 - min_green,
        "4G": 16,
    }


try:
    PARAMS = generate_default_params()

    RECEIVED_PARAMS = nni.get_next_parameter()
    # test = {"parameter_id": "3_0_0", "parameter_source": "algorithm", "parameters": {"min1": 8, "min2": 8, "min3": 3, "min4": 6, "priority1": 8, "priority2": 4, "priority3": 8, "priority4": 3, "release1": 3, "release2": 7, "release3": 7, "release4": 5, "weight1": 0.3507279901255561, "weight2": 0.41063724881243446, "weight3": 0.3002143868929728, "weight4": 0.26262657920838317, "TRIAL_BUDGET": 1}}
    # RECEIVED_PARAMS = test['parameters']

    PARAMS.update(RECEIVED_PARAMS)

    train(PARAMS)

except:
    print(traceback.format_exc())
    print("Something else went wrong")
