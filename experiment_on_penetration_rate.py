# -*- coding: utf-8 -*-
import glob
import json

import numpy as np

import test_adaptive, test_fixed
import matplotlib.pyplot as plt


def main():
    # repeat_adaptive()
    # repeat_fixed_time()
    loss_list_by_penetration_rate = do_statistic('adaptive')
    loss_list_by_penetration_rate.update(do_statistic('fixed'))

    plot(loss_list_by_penetration_rate)
    print(1 - np.mean(loss_list_by_penetration_rate[1.0]) / np.mean(loss_list_by_penetration_rate['fixed']))


def repeat_adaptive():
    for idx in range(1, 11):
        p = idx / 10
        for exp_idx in range(10):
            test_adaptive.debug = False
            test_adaptive.main(p)


def repeat_fixed_time():
    for exp_idx in range(10):
        test_fixed.debug = False
        test_fixed.main()


def do_statistic(experiment_type: str):
    loss_list_by_penetration_rate = {}
    for filename in glob.glob(f'output/{experiment_type}/*.json'):
        with open(filename) as data_file:
            params_by_junction_name = json.load(data_file)
        loss = 0
        penetration_rate = None
        for junction_name, params in params_by_junction_name.items():
            penetration_rate = params.get('penetration_rate', 'fixed')
            loss += params['total_time_loss']
        loss_list_by_penetration_rate.setdefault(penetration_rate, []).append(loss)
    print(f'{experiment_type}: {loss_list_by_penetration_rate}')
    return loss_list_by_penetration_rate


def plot(loss_list_by_penetration_rate):
    res = {_: loss_list_by_penetration_rate[_]
           for _ in sorted(loss_list_by_penetration_rate,
                           key=lambda x: sum(loss_list_by_penetration_rate[x]),
                           reverse=True)}

    plt.figure(figsize=(8, 6))
    plt.boxplot(res.values(),
                labels=[str(_) for _ in res])
    plt.ylabel('total time loss (s)')
    plt.xlabel('penetration rate/fixed-time plan')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
