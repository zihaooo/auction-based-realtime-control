# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import random
import time

from utils.Junction import JunctionAdaptive
from utils.Sim import SimAdaptive


def main(penetration_rate=1, delay=0):
    config_dir = 'configs'
    fixed_plan_dir = f'{config_dir}/plans'
    constants_config_dir = f'{config_dir}/constants'
    sumo_template_dir = 'sumo_files'
    time.sleep(delay*2)
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
        '--waiting-time-memory', '14400',
        '--no-warnings', 'true',
        '--random',
        '--tripinfo-output', trip_output_filename
    ]

    adaptive_step_size = 2

    junction_list = [
        JunctionAdaptive(junction_name='Huron',
                         junction_id='cluster_62477163_62500824',
                         fixed_plan_filename=f'{fixed_plan_dir}/Huron.json',
                         constants_filename=f'{constants_config_dir}/Huron.json',
                         count_down_step=step,
                         adaptive_step_size=adaptive_step_size,
                         offset=26),
        JunctionAdaptive(junction_name='Green',
                         junction_id='62606176',
                         fixed_plan_filename=f'{fixed_plan_dir}/Green.json',
                         constants_filename=f'{constants_config_dir}/Green.json',
                         count_down_step=step,
                         adaptive_step_size=adaptive_step_size,
                         offset=88)
    ]

    output_dir = 'output/adaptive'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    log_dir = f'{output_dir}/logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    report_filename = f'{output_dir}/{int(time.time() * 1000)}_{random.randint(0, 99):0d}.json'
    phase_log_filename = f'{log_dir}/phase.log'

    sim = SimAdaptive(junction_list, cmd, detector_output_filename, trip_output_filename, report_filename,
                      penetration_rate)
    sim.control()
    sim.close()
    report = sim.report(phase_log_filename)

    os.system(f'rm -rf {sumo_test_dir}')
    return report


debug = False
if __name__ == '__main__':
    main()
