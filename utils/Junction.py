# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from copy import deepcopy
from typing import Dict, List, Tuple
from . import traci

import gurobipy as gp


class JunctionBase:
    def __init__(self,
                 junction_name: str,
                 junction_id: str,
                 count_down_step: float):
        self.junction_name = junction_name
        self.junction_id = junction_id
        self.count_down_step: float = count_down_step
        self.phase_log: Tuple[List[float], List[str]] = ([], [])


class JunctionAuctionBased(JunctionBase):
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
        self.observed_veh_set = set()
        self.init_loss_time_by_veh = {}
        self.accumulate_loss_time_by_veh = {}
        self.time_loss_list_by_phase = {}

        self.last_change_ts = 0
        self.current_phase = '1'
        self.next_phase = '2'

        self.yellow_count_down: float = 0
        self.ar_count_down: float = 0

    def update_phase_time_loss_list_by_veh(self, veh: str):
        route = traci.vehicle.getRouteID(veh).split('_')[1]
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
                 fixed_plan_filename: str):
        super().__init__(junction_name, junction_id, count_down_step)

        with open(fixed_plan_filename) as data_file:
            fixed_plan = json.load(data_file)
        self.effective_green = fixed_plan['effective_green']
        self.green_by_phase = fixed_plan['green_by_phase']


class JunctionAdaptive(JunctionBase):
    def __init__(self,
                 junction_name: str,
                 junction_id: str,
                 count_down_step: float,
                 fixed_plan_filename: str,
                 constants_filename: str,
                 adaptive_step_size: float,
                 offset: float):
        super().__init__(junction_name, junction_id, count_down_step)

        with open(constants_filename) as data_file:
            constants = json.load(data_file)
        self.yellow_by_phase = constants['yellow_by_phase']
        self.ar_by_phase = constants['ar_by_phase']
        self.signal_by_phase = constants['signal_by_phase']
        self.phase_sequence = sorted(self.signal_by_phase.keys())
        self.edge_list = constants['edge_list']
        self.route_set = set()
        self.phase_by_route = {}
        for phase, route_list in constants['route_list_by_phase'].items():
            for route in route_list:
                self.route_set.add(route)
                self.phase_by_route[route] = phase
        self.movement_by_route = {}
        for movement, route_list in constants['route_list_by_movement'].items():
            for route in route_list:
                self.movement_by_route[route] = movement
        self.movement_list = sorted(set(self.movement_by_route.values()))

        self.movement_list_by_phase = {
            "1": ["2", "6"],
            "2": ["1", "5"],
            "3": ["4", "8"],
            "4": ["3", "7"]
        }

        with open(fixed_plan_filename) as data_file:
            fixed_plan = json.load(data_file)
        self.original_green_by_phase = deepcopy(fixed_plan['green_by_phase'])
        self.green_by_phase = fixed_plan['green_by_phase']
        self.effective_green = fixed_plan['effective_green']
        self.min_green = fixed_plan.get('min_green', 4)
        self.adaptive_step_size = adaptive_step_size

        self.green_by_movement = {}
        self.update_green_by_movement()
        self.original_green_by_movement = deepcopy(self.green_by_movement)

        self.veh_set = set()
        self.route_by_veh = {}
        self.observed_veh_set = set()
        self.veh_state_by_veh = {}
        self.init_stop_delay_by_veh = {}
        self.init_stop_num_by_veh = {}
        self.accumulate_stop_num_by_veh = {}
        self.accumulate_stop_delay_by_veh = {}

        self.last_change_ts = 0
        offset = 120 - offset
        t_in_c = 0
        for phase in self.phase_sequence:
            t_in_c += self.green_by_phase[phase] + self.yellow_by_phase[phase] + self.ar_by_phase[phase]
            if t_in_c >= offset:
                self.current_phase = phase
                break
        res = t_in_c - offset
        if res < self.ar_by_phase[self.current_phase]:
            self.ar_count_down: float = res
            self.yellow_count_down: float = 0
            self.green_count_down: float = 0
        else:
            self.ar_count_down: float = self.ar_by_phase[self.current_phase]
            res -= self.ar_by_phase[self.current_phase]
            if res < self.yellow_by_phase[self.current_phase]:
                self.yellow_count_down: float = res
                self.green_count_down: float = 0
            else:
                self.yellow_count_down: float = self.yellow_by_phase[self.current_phase]
                res -= self.yellow_by_phase[self.current_phase]
                self.green_count_down: float = res

        self.at_the_end_of_cycle = False
        self.gp_env = gp.Env()
        self.gp_env.setParam('OutputFlag', 0)

    def update_green_by_movement(self):
        self.green_by_movement = {}
        for phase, movement_list in self.movement_list_by_phase.items():
            for movement in movement_list:
                self.green_by_movement[movement] = self.green_by_phase[phase]

    def count_down(self):
        self.at_the_end_of_cycle = False
        if self.green_count_down > 0:
            traci.trafficlight.setRedYellowGreenState(self.junction_id,
                                                      self.signal_by_phase[self.current_phase]['g'])
            self.green_count_down = max(0.0, self.green_count_down - self.count_down_step)
            if self.green_count_down == 0:
                traci.trafficlight.setRedYellowGreenState(self.junction_id,
                                                          self.signal_by_phase[self.current_phase]['y'])
            return
        if self.yellow_count_down > 0:
            self.yellow_count_down = max(0.0, self.yellow_count_down - self.count_down_step)
            if self.yellow_count_down == 0:
                traci.trafficlight.setRedYellowGreenState(self.junction_id,
                                                          self.signal_by_phase[self.current_phase]['ar'])
            return
        if self.ar_count_down > 0:
            self.ar_count_down = max(0.0, self.ar_count_down - self.count_down_step)
            if self.ar_count_down == 0:
                next_phase_idx = (self.phase_sequence.index(self.current_phase) + 1) % len(self.phase_sequence)
                self.current_phase = self.phase_sequence[next_phase_idx]
                traci.trafficlight.setRedYellowGreenState(self.junction_id,
                                                          self.signal_by_phase[self.current_phase]['g'])
                self.green_count_down = self.green_by_phase[self.current_phase]
                self.yellow_count_down = self.yellow_by_phase[self.current_phase]
                self.ar_count_down = self.ar_by_phase[self.current_phase]
                if next_phase_idx == 0:
                    self.at_the_end_of_cycle = True
                self.last_change_ts = traci.simulation.getTime()
                self.phase_log[0].append(self.last_change_ts)
                self.phase_log[1].append(self.current_phase)
            return

    def calc_new_green_time(self):
        ov_num_by_movement = {}
        ov_delay_by_movement = {}
        u_num_by_movement = {}
        u_delay_by_movement = {}
        for veh in self.observed_veh_set:
            route = self.route_by_veh[veh]
            movement = self.movement_by_route[route]
            stop_num = self.accumulate_stop_num_by_veh[veh] - self.init_stop_num_by_veh[veh]
            stop_delay = self.accumulate_stop_delay_by_veh[veh] - self.init_stop_delay_by_veh[veh]
            if stop_num > 1:
                ov_num_by_movement[movement] = ov_num_by_movement.get(movement, 0) + 1
                ov_delay_by_movement[movement] = ov_delay_by_movement.get(movement, 0) + stop_delay
            else:
                u_num_by_movement[movement] = u_num_by_movement.get(movement, 0) + 1
                u_delay_by_movement[movement] = u_delay_by_movement.get(movement, 0) + stop_delay
        total_ov_num = sum(ov_num_by_movement.values()) + 1e-10
        total_ov_delay = sum(ov_delay_by_movement.values()) + 1e-10
        total_u_num = sum(u_num_by_movement.values()) + 1e-10
        total_u_delay = sum(u_delay_by_movement.values()) + 1e-10

        weight_by_movement = {}
        for movement in self.movement_list:
            if movement in ov_num_by_movement:
                weight = 1 + ov_num_by_movement[movement] / total_ov_num \
                         * ov_delay_by_movement[movement] / total_ov_delay
            else:
                u_num, u_delay = u_num_by_movement.get(movement, 0), u_delay_by_movement.get(movement, 0)
                if self.green_by_movement[movement] > self.original_green_by_movement[movement]:
                    weight = -(1 - u_num / total_u_num) * (1 - u_delay / total_u_delay)
                else:
                    weight = u_num / total_u_num * u_delay / total_u_delay
            weight_by_movement[movement] = \
                weight * (ov_num_by_movement.get(movement, 0) + u_num_by_movement.get(movement, 0)) / (
                    total_u_num + total_ov_num)

        int_coef = 2
        model = gp.Model('opt-green', env=self.gp_env)
        phase_num = len(self.phase_sequence)
        movement_num = len(self.movement_list)
        g_s = model.addVars(phase_num, ub=200, vtype=gp.GRB.INTEGER)
        g_m = model.addVars(movement_num, ub=200, vtype=gp.GRB.INTEGER)
        model.addConstrs(
            ((g_m[int(m) - 1] - self.original_green_by_movement[m]) * int_coef <= self.adaptive_step_size * int_coef
             for m in self.movement_list), name='step limit 1/2')
        model.addConstrs(
            ((g_m[int(m) - 1] - self.original_green_by_movement[m]) * int_coef >= -self.adaptive_step_size * int_coef
             for m in self.movement_list), name='step limit 2/2')

        for s, m_list in self.movement_list_by_phase.items():
            model.addConstr(g_s[int(s) - 1] >= self.min_green)
            for m in m_list:
                model.addConstr(g_m[int(m) - 1] == g_s[int(s) - 1])
        model.addConstr(gp.quicksum(g_s[i] for i in range(phase_num)) == self.effective_green, name='cycle no change')
        model.setObjective(gp.quicksum(weight_by_movement[m] * (g_m[int(m) - 1] - self.green_by_movement[m])
                                       for m in self.movement_list), gp.GRB.MAXIMIZE)
        model.optimize()

        for p in range(phase_num):
            phase = self.phase_sequence[p]
            self.green_by_phase[phase] = g_s[p].x

        self.green_count_down = self.green_by_phase['1']

        if self.junction_name == 'Huron':
            # print(self.junction_name, self.green_by_phase.values())
            print('\t'.join(map(str, self.green_by_phase.values())))

        self.update_green_by_movement()
