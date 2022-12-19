# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import random
import time

from utils.Junction import JunctionFixed
from utils.Sim import SimFixed


def main(delay=0):
    config_dir = 'configs'
    sumo_template_dir = 'sumo_files'
    time.sleep(delay*2)
    tmp_str = f'{int(time.time() * 1000000)}_{random.randint(0, 99):0d}'
    sumo_test_dir = f'sumo_{tmp_str}'.replace(' ', '_')
    os.system(f'cp -r {sumo_template_dir} {sumo_test_dir}')

    detector_output_filename = f'{sumo_test_dir}/e3output.xml'
    trip_output_filename = f'{sumo_test_dir}/output.xml'
    sumo_config_filename = f'{sumo_test_dir}/osm.sumocfg'
    sumo_net_filename = f'{sumo_test_dir}/osm.net.xml'

    sumo_bin = 'sumo-gui' if debug else 'sumo'
    step = 0.5
    cmd = [
        sumo_bin,
        '-c', sumo_config_filename,
        '--step-length', f'{step}',
        '--no-warnings', 'true',
        '--random',
        '--duration-log.statistics',
        '--tripinfo-output', trip_output_filename
    ]
    fixed_plan_dir = f'{config_dir}/plans'
    junction_list = [
        JunctionFixed(junction_name='Huron',
                      junction_id='cluster_62477163_62500824',
                      fixed_plan_filename=f'{fixed_plan_dir}/Huron.json',
                      count_down_step=step),
        JunctionFixed(junction_name='Green',
                      junction_id='62606176',
                      fixed_plan_filename=f'{fixed_plan_dir}/Green.json',
                      count_down_step=step)
    ]

    output_dir = 'output/fixed'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    report_filename = f'{output_dir}/{tmp_str}.json'

    sim = SimFixed(junction_list, cmd, detector_output_filename, trip_output_filename, report_filename,
                   sumo_net_filename)
    sim.control()
    sim.close()
    report = sim.report()

    os.system(f'rm -rf {sumo_test_dir}')
    return report


debug = False
if __name__ == '__main__':
    main()
