# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import random
import time

from utils.Junction import Junction
from utils.Sim import Sim


def main():
    config_dir = 'configs'
    control_config_dir = f'{config_dir}/params'
    constants_config_dir = f'{config_dir}/constants'
    sumo_dir = 'sumo_files'
    detector_output_filename = f'{sumo_dir}/e3output.xml'
    sumo_config_filename = f'{sumo_dir}/osm.sumocfg'
    sumo_bin = 'sumo-gui' if debug else 'sumo'
    step = 0.5
    cmd = [
        sumo_bin,
        '-c', sumo_config_filename,
        '--step-length', f'{step}']
    junction_list = [
        Junction(junction_name='Huron',
                 junction_id='cluster_62477163_62500824',
                 params_filename=f'{control_config_dir}/Huron.json',
                 constants_filename=f'{constants_config_dir}/Huron.json',
                 count_down_step=step),
        Junction(junction_name='Green',
                 junction_id='62606176',
                 params_filename=f'{control_config_dir}/Green.json',
                 constants_filename=f'{constants_config_dir}/Green.json',
                 count_down_step=step)
    ]

    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    report_filename = f'{output_dir}/{int(time.time() * 1000)}_{random.randint(0, 99):0d}.json'

    sim = Sim(junction_list, cmd, detector_output_filename, report_filename)
    sim.control()
    sim.close()
    sim.report()


if __name__ == '__main__':
    debug = True
    main()
