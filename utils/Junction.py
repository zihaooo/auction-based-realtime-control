# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Dict, List, Tuple
from . import traci


class JunctionBase:
    def __init__(self,
                 junction_name: str,
                 junction_id: str,
                 count_down_step: float):
        self.junction_name = junction_name
        self.junction_id = junction_id
        self.count_down_step: float = count_down_step
        self.phase_log: Tuple[List[float], List[str]] = ([], [])


class JunctionAdaptive(JunctionBase):
    def __init__(self,
                 junction_name: str,
                 junction_id: str,
                 count_down_step: float,
                 constants_filename: str,
                 params_filename: str):
        super().__init__(junction_name, junction_id, count_down_step)

        with open(constants_filename) as data_file:
            constants = json.load(data_file)
        self.yellow_by_phase = constants['yellow_by_phase']
        self.ar_by_phase = constants['ar_by_phase']
        self.signal_by_phase = constants['signal_by_phase']
        self.edge_list = constants['edge_list']
        self.route_set = set()
        self.phase_by_route = {}
        for phase, route_list in constants['route_list_by_phase'].items():
            for route in route_list:
                self.route_set.add(route)
                self.phase_by_route[route] = phase

        with open(params_filename) as data_file:
            params = json.load(data_file)
        self.duration_by_phase = params['duration_by_phase']
        self.weight_by_phase = params['weight_by_phase']

        self.veh_set = set()
        self.init_loss_time_by_veh = {}
        self.accumulate_loss_time_by_veh = {}
        self.time_loss_list_by_phase = {}

        self.last_change_ts = 0
        self.current_phase = '1'
        self.next_phase = '2'

        self.yellow_count_down: float = 0
        self.ar_count_down: float = 0

    def update_phase_time_loss_list_by_veh(self, veh: str):
        route = veh.split('_')[-1].split('.')[0]
        phase = self.phase_by_route[route]
        time_loss = self.accumulate_loss_time_by_veh[veh] - self.init_loss_time_by_veh[veh]
        self.time_loss_list_by_phase.setdefault(phase, []).append(time_loss)

    def reset_phase_time_loss(self):
        self.time_loss_list_by_phase = {}

    def calc_bid(self) -> Dict[str, float]:
        return {
            phase: sum(time_loss_list) * self.weight_by_phase[phase]
            for phase, time_loss_list in self.time_loss_list_by_phase.items()
        }

    def change_phase(self, next_phase: str):
        self.next_phase = next_phase
        self.yellow_count_down = self.yellow_by_phase[self.current_phase]
        self.ar_count_down = self.ar_by_phase[self.current_phase]
        traci.trafficlight.setRedYellowGreenState(self.junction_id, self.signal_by_phase[self.current_phase]['y'])

    def in_phase_transition(self):
        if self.yellow_count_down != 0.0:
            self.yellow_count_down = max(0.0, self.yellow_count_down - self.count_down_step)
            if self.yellow_count_down == 0.0:
                traci.trafficlight.setRedYellowGreenState(self.junction_id,
                                                          self.signal_by_phase[self.current_phase]['ar'])
            return True

        if self.ar_count_down != 0.0:
            self.ar_count_down = max(0.0, self.ar_count_down - self.count_down_step)
            if self.ar_count_down == 0.0:
                self.current_phase = self.next_phase
                traci.trafficlight.setRedYellowGreenState(self.junction_id,
                                                          self.signal_by_phase[self.current_phase]['g'])
                self.last_change_ts = traci.simulation.getTime()
                self.phase_log[0].append(self.last_change_ts)
                self.phase_log[1].append(self.current_phase)
            return True

        return False


class JunctionFixed(JunctionBase):
    def __init__(self,
                 junction_name: str,
                 junction_id: str,
                 count_down_step: float,
                 fixed_plan_filename: str = None):
        super().__init__(junction_name, junction_id, count_down_step)

        with open(fixed_plan_filename) as data_file:
            fixed_plan = json.load(data_file)
        self.effective_green = fixed_plan['effective_green']
        self.green_by_phase = fixed_plan['green_by_phase']
