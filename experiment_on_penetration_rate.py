# -*- coding: utf-8 -*-
import glob
import json
from multiprocessing import Pool, cpu_count

import numpy as np

import test_adaptive, test_auction_based, test_fixed
import matplotlib.pyplot as plt
import matplotlib as mpl

label_size = 16
mpl.rcParams['xtick.labelsize'] = label_size
mpl.rcParams['ytick.labelsize'] = label_size


def main():
    # repeat_auction_based()
    repeat_fixed_time()
    repeat_adaptive()
    fixed_metric = do_statistic('fixed')
    metric_by_name = do_statistic('adaptive')
    y_label_by_metric_name = {
        'junction_loss': 'total junction time loss (s)',
        'stop_num': 'avg stop num per trip',
        'stop_delay': 'avg stop delay per trip (s)',
        'time_loss': 'avg time loss per trip (s)'
    }
    for metric_name, metric_by_penetration_rate in metric_by_name.items():
        if metric_name != 'veh_num_lists':
            metric_by_penetration_rate.update(fixed_metric[metric_name])
            plot(metric_by_penetration_rate, y_label=y_label_by_metric_name[metric_name], name=metric_name)
        else:
            plot_veh_num(metric_by_penetration_rate)


def change_route_file(i):
    old_route_file = f'osm_{i}.rou.xml'
    new_route_file = f'osm_{i + 2}.rou.xml'
    with open('sumo_files/osm.sumocfg', 'r') as r_file:
        config = r_file.read()
    with open('sumo_files/osm.sumocfg', 'w') as w_file:
        w_file.write(config.replace(old_route_file, new_route_file))


def repeat_auction_based():
    for idx in range(1, 11):
        p = idx / 10
        for exp_idx in range(20):
            test_auction_based.main(p)


def repeat_fixed_time():
    with Pool(cpu_count()) as pool:
        pool.map(test_fixed.main, range(40))


def repeat_adaptive():
    args = [(p, delay) for p in [0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1] for delay in range(40)]
    with Pool(cpu_count()) as pool:
        pool.starmap(test_adaptive.main, args)


def do_statistic(experiment_type: str):
    loss_list_by_penetration_rate = {}
    stop_num_list_by_penetration_rate = {}
    stop_delay_list_by_penetration_rate = {}
    time_loss_list_by_penetration_rate = {}
    veh_num_lists = []
    for idx, filename in enumerate(sorted(glob.glob(f'output/{experiment_type}/*.json'))):
        with open(filename) as data_file:
            params_by_junction_name = json.load(data_file)

        loss = 0
        penetration_rate = None
        for junction_name, params in params_by_junction_name.items():
            if junction_name in ['trip_avg', 'veh_num_list']:
                continue
            penetration_rate = params.get('penetration_rate', 'fixed')
            loss += params['total_time_loss']
        loss_list_by_penetration_rate.setdefault(penetration_rate, []).append(loss)
        stop_num_list_by_penetration_rate.setdefault(penetration_rate, []) \
            .append(params_by_junction_name['trip_avg']['stop_num'])
        stop_delay_list_by_penetration_rate.setdefault(penetration_rate, []) \
            .append(params_by_junction_name['trip_avg']['stop_delay'])
        time_loss_list_by_penetration_rate.setdefault(penetration_rate, []) \
            .append(params_by_junction_name['trip_avg']['time_loss'])
        if experiment_type == 'adaptive':
            veh_num_lists.append(params_by_junction_name['veh_num_list'])

    print(f'{experiment_type}: {loss_list_by_penetration_rate}')
    print(experiment_type)
    return {
        'junction_loss': loss_list_by_penetration_rate,
        'stop_num': stop_num_list_by_penetration_rate,
        'stop_delay': stop_delay_list_by_penetration_rate,
        'time_loss': time_loss_list_by_penetration_rate,
        'veh_num_lists': veh_num_lists
    }


def plot(metric_list_by_penetration_rate, y_label: str, name: str = None):
    res = {'fixed': metric_list_by_penetration_rate['fixed']}
    res.update({f'{_ * 100:.1f}%' if _ < 0.09 else f'{_ * 100:.0f}%': metric_list_by_penetration_rate[_]
                for _ in sorted(metric_list_by_penetration_rate, key=lambda x: str(x)) if _ != 'fixed'})

    plt.figure(figsize=(8, 6))
    plt.boxplot(res.values(),
                labels=[str(_) for _ in res])
    plt.ylabel(y_label, fontsize=20)
    plt.xlabel('fixed-time plan/penetration rate', fontsize=20)
    plt.tight_layout()
    # plt.show()
    if name:
        plt.savefig(f'figures/sim_{name}.png', dpi=200)
        ref = np.median(metric_list_by_penetration_rate['fixed'])
        print(name)
        for p, tr_list in res.items():
            print(p, f'{(np.median(tr_list) / ref - 1) * 100:.1f}')


def plot_veh_num(veh_num_lists):
    total_time = 14400
    cycle = 120
    num_cycle = total_time // cycle
    veh_num_np = np.array([_[:num_cycle] for _ in veh_num_lists])
    mean_np = np.mean(veh_num_np, axis=0)
    std_np = np.std(veh_num_np, axis=0)
    x = [i * cycle for i in range(num_cycle)]
    plt.figure(figsize=(8, 6))
    plt.plot(x, mean_np, color='b')
    plt.fill_between(x, mean_np - std_np, mean_np + std_np, alpha=0.15, color='b')
    plt.xlabel('time in simulation (s)', fontsize=20)
    plt.ylabel('# of veh in scene', fontsize=20)
    plt.tight_layout()
    plt.savefig('figures/sim_veh_num.png', dpi=200)


if __name__ == "__main__":
    main()
