# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import random
import time

from utils.Junction import JunctionAuctionBased
from utils.Sim import SimAuctionBased


def main(penetration_rate=1.0):
    config_dir = 'configs'
    control_config_dir = f'{config_dir}/params'
    constants_config_dir = f'{config_dir}/constants'

    sumo_template_dir = 'sumo_files'
    tmp_str = f'{int(time.time() * 1000000)}_{random.randint(0, 99):0d}'
    sumo_test_dir = f'sumo_{tmp_str}'.replace(' ', '_')
    os.system(f'cp -r {sumo_template_dir} {sumo_test_dir}')

    detector_output_filename = f'{sumo_test_dir}/e3output.xml'
    trip_output_filename = f'{sumo_test_dir}/output.xml'
    sumo_config_filename = f'{sumo_test_dir}/osm.sumocfg'

    sumo_bin = 'sumo-gui' if debug else 'sumo'
    step = 0.5
    cmd = [
        sumo_bin,
        '-c', sumo_config_filename,
        '--step-length', f'{step}',
        '--duration-log.statistics',
        '--random',
        '--tripinfo-output', f'{sumo_test_dir}/output.xml'
    ]
    junction_list = [
        JunctionAuctionBased(junction_name='Huron',
                             junction_id='cluster_62477163_62500824',
                             params_filename=f'{control_config_dir}/Huron.json',
                             constants_filename=f'{constants_config_dir}/Huron.json',
                             count_down_step=step),
        JunctionAuctionBased(junction_name='Green',
                             junction_id='62606176',
                             params_filename=f'{control_config_dir}/Green.json',
                             constants_filename=f'{constants_config_dir}/Green.json',
                             count_down_step=step)
    ]

    output_dir = 'output/auction_based'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    log_dir = f'{output_dir}/logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    report_filename = f'{output_dir}/{int(time.time() * 1000)}_{random.randint(0, 99):0d}.json'
    phase_log_filename = f'{log_dir}/phase.log'

    sim = SimAuctionBased(junction_list, cmd, detector_output_filename, trip_output_filename, report_filename,
                          penetration_rate)
    sim.control()
    sim.close()
    report = sim.report(phase_log_filename)

    os.system(f'rm -rf {sumo_test_dir}')
    return report


if __name__ == '__main__':
    debug = False
    main()
