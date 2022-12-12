# -*- coding: utf-8 -*-
import json
from typing import Dict, Any

import numpy as np


def main():
    analysis('Huron')
    analysis('Green')


def analysis(junction_name: str):
    with open('logs/auction_based/phase.log') as data_file:
        phase_log_by_junction_name = json.load(data_file)
    phase_log = phase_log_by_junction_name[junction_name]
    analysis_cycle(phase_log)
    analysis_sequence(phase_log)
    analysis_green_split(phase_log)


def analysis_cycle(phase_log: Dict[str, Any]):
    phase_start_t_list = phase_log['phase_start_t']
    phase_list = phase_log['phase']
    phase_1_start_list = []
    for start_t, phase in zip(phase_start_t_list, phase_list):
        if phase == '1':
            phase_1_start_list.append(start_t)
    phase_1_start_np = np.array(phase_1_start_list)
    pseudo_cycle_np = np.diff(phase_1_start_np)
    print(f'mean: {np.mean(pseudo_cycle_np):.1f}, std: {np.std(pseudo_cycle_np):.1f}')


def analysis_sequence(phase_log: Dict[str, Any]):
    phase_list = phase_log['phase']
    next_phase_count_by_phase = {}
    for phase, next_phase in zip(phase_list[0:-1], phase_list[1:]):
        next_phase_count_by_phase.setdefault(phase, {next_phase: 0})
        next_phase_count_by_phase[phase][next_phase] = next_phase_count_by_phase[phase].get(next_phase, 0) + 1
    next_phase_freq_by_phase = {}
    for phase, next_phase_count in next_phase_count_by_phase.items():
        total = sum(next_phase_count.values())
        for next_phase, count in next_phase_count.items():
            next_phase_freq_by_phase.setdefault(phase, {next_phase: f'{count / total * 100:.0f}%'})
            next_phase_freq_by_phase[phase][next_phase] = f'{count / total * 100:.0f}%'
    print(next_phase_freq_by_phase)


def analysis_green_split(phase_log: Dict[str, Any]):
    phase_start_t_list = phase_log['phase_start_t']
    phase_list = phase_log['phase']
    phase_length_list = np.diff(phase_start_t_list)
    phase_list = phase_list[:-1]
    phase_length_list_by_phase = {}
    for phase, phase_length in zip(phase_list, phase_length_list):
        phase_length_list_by_phase.setdefault(phase, []).append(phase_length)

    for phase, phase_length_list in phase_length_list_by_phase.items():
        print(f'phase: {phase}, mean: {np.mean(phase_length_list):.1f}, std: {np.std(phase_length_list):.1f}')


if __name__ == "__main__":
    main()
