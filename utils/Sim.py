# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import List
from xml.etree import ElementTree as et

import libsumo as traci

from utils.Junction import Junction


class Sim:
    def __init__(self, junction_list: List[Junction],
                 cmd: List[str],
                 detector_output_file: str,
                 report_filename: str):
        self.junction_list: List[Junction] = junction_list
        self.report_filename = report_filename
        self.det_output_file = detector_output_file
        traci.start(cmd)

    @staticmethod
    def get_current_ts():
        return traci.simulation.getTime()

    @staticmethod
    def run():
        traci.simulationStep()

    def update_traffic_state(self):
        veh_list = traci.vehicle.getIDList()
        for veh in veh_list:
            lane_id = traci.vehicle.getLaneID(veh)
            if not lane_id:
                continue
            route = veh.split('_')[-1].split('.')[0]
            edge_id = lane_id.split('_')[0]
            junction: Junction | None = None
            for _junction in self.junction_list:
                if route not in _junction.route_set:
                    continue
                if edge_id in _junction.edge_list:
                    junction = _junction
                    break
                if veh in _junction.veh_set:
                    _junction.veh_set.remove(veh)
                    del _junction.init_loss_time_by_veh[veh]
                    del _junction.accumulate_loss_time_by_veh[veh]
            if junction is None:
                continue
            loss_time = traci.vehicle.getTimeLoss(veh)
            if veh not in junction.veh_set:
                junction.init_loss_time_by_veh[veh] = loss_time
                junction.veh_set.add(veh)
            junction.accumulate_loss_time_by_veh[veh] = loss_time
        for junction in self.junction_list:
            junction.reset_phase_time_loss()
            for veh in junction.veh_set:
                junction.update_phase_time_loss_list_by_veh(veh)

    @staticmethod
    def has_veh() -> bool:
        return traci.simulation.getMinExpectedNumber() > 0

    @staticmethod
    def close():
        traci.close()

    def report(self):
        tree = et.parse(self.det_output_file)
        root = tree.getroot()
        time_loss_list_by_junction_name = {}
        total_loss_by_junction_name = {}
        for bound in root:
            if bound.get('begin') != '0.00':
                continue
            bound_id = bound.get('id')
            junction_name = None
            for junction in self.junction_list:
                if junction.junction_id in bound_id:
                    junction_name = junction.junction_name
                    break
            num = float(bound.get('vehicleSum'))
            mean_loss = float(bound.get('meanTimeLoss'))
            time_loss = num * mean_loss
            time_loss_list_by_junction_name.setdefault(junction_name, []).append(time_loss)
            total_loss_by_junction_name[junction_name] = total_loss_by_junction_name.get(junction_name, 0) + time_loss

        report = {}
        for junction in self.junction_list:
            junction_name = junction.junction_name
            report[junction_name] = {
                'total_time_loss': total_loss_by_junction_name[junction_name],
                'duration_by_phase': junction.duration_by_phase,
                'weight_by_phase': junction.weight_by_phase
            }

        with open(self.report_filename, 'w') as data_file:
            json.dump(report, data_file, indent=2)

    def control(self):
        while self.has_veh():
            self.run()
            current_ts = self.get_current_ts()
            self.update_traffic_state()

            for junction in self.junction_list:
                if junction.in_phase_transition():
                    continue
                duration_by_type = junction.duration_by_phase[junction.current_phase]
                bid_by_phase = junction.calc_bid()
                bid_phase_list = [k for k, v in bid_by_phase.items() if v > 0]
                if not bid_phase_list:
                    continue
                duration = current_ts - junction.last_change_ts
                if not duration >= duration_by_type['min']:
                    continue

                if not duration >= duration_by_type['min'] + duration_by_type['priority']:
                    if junction.current_phase in bid_phase_list:
                        continue

                    # todo: round-robin
                    next_phase = max(bid_by_phase, key=bid_by_phase.get)
                    if next_phase == junction.current_phase:
                        continue
                    junction.change_phase(next_phase)
                    continue
                if bid_phase_list == [junction.current_phase] or not bid_phase_list:
                    continue

                if duration >= sum(duration_by_type.values()):
                    bid_by_phase[junction.current_phase] = 0

                next_phase = max(bid_by_phase, key=bid_by_phase.get)
                if next_phase == junction.current_phase:
                    continue
                junction.change_phase(next_phase)

