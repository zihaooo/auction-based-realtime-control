# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import random
from typing import List
from xml.etree import ElementTree as et

from . import traci

from utils.Junction import JunctionFixed, JunctionAuctionBased, JunctionAdaptive


class SimBase:
    def __init__(self, junction_list: List[JunctionFixed | JunctionAuctionBased | JunctionAdaptive],
                 detector_output_file: str, trip_output_filename: str, report_filename: str):
        self.junction_list: List[JunctionFixed | JunctionAuctionBased | JunctionAdaptive] = junction_list
        self.report_filename = report_filename
        self.det_output_file = detector_output_file
        self.trip_output_filename = trip_output_filename
        self.total_loss_by_junction_name = {}

    @staticmethod
    def get_current_ts():
        return traci.simulation.getTime()

    @staticmethod
    def run():
        traci.simulationStep()

    @staticmethod
    def has_veh() -> bool:
        return traci.simulation.getMinExpectedNumber() > 0

    @staticmethod
    def close():
        traci.close()

    def calc_loss(self):
        tree = et.parse(self.det_output_file)
        root = tree.getroot()
        time_loss_list_by_junction_name = {}
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
            total_loss = self.total_loss_by_junction_name.get(junction_name, 0)
            self.total_loss_by_junction_name[junction_name] = total_loss + time_loss
        return self.total_loss_by_junction_name

    def calc_trips_statistics(self):
        total_veh_num = 0
        total_stop_num = 0
        total_stop_delay = 0
        total_loss_time = 0
        tree = et.parse(self.trip_output_filename)
        root = tree.getroot()
        for trip in root:
            total_veh_num += 1
            total_stop_delay += float(trip.get('waitingTime'))
            total_stop_num += float(trip.get('waitingCount'))
            total_loss_time += float(trip.get('timeLoss'))
        return {
            'stop_num': total_stop_num / total_veh_num,
            'stop_delay': total_stop_delay / total_veh_num,
            'time_loss': total_loss_time / total_veh_num
        }

    def report(self, *args, **kwargs):
        pass

    def control(self):
        pass


class SimAuctionBased(SimBase):
    def __init__(self, junction_list: List[JunctionAuctionBased],
                 cmd: List[str],
                 detector_output_file: str,
                 trip_output_filename: str,
                 report_filename: str,
                 penetration_rate: float = 1.0):
        super().__init__(junction_list, detector_output_file, trip_output_filename, report_filename)
        traci.start(cmd)
        self.penetration_rate = penetration_rate
        self.observed_veh_set = set()

    def update_traffic_state(self):
        veh_list = traci.vehicle.getIDList()
        for veh in veh_list:
            lane_id = traci.vehicle.getLaneID(veh)
            if not lane_id:
                continue
            route = traci.vehicle.getRouteID(veh).split('_')[1]
            edge_id = lane_id.split('_')[0]
            junction: JunctionAuctionBased | None = None
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
                    if veh in _junction.observed_veh_set:
                        _junction.observed_veh_set.remove(veh)
            if junction is None:
                continue
            loss_time = traci.vehicle.getTimeLoss(veh)
            if veh not in junction.veh_set:
                junction.init_loss_time_by_veh[veh] = loss_time
                junction.veh_set.add(veh)
                if random.random() >= 1 - self.penetration_rate:
                    junction.observed_veh_set.add(veh)
            junction.accumulate_loss_time_by_veh[veh] = loss_time
        for junction in self.junction_list:
            junction.reset_phase_time_loss()
            for veh in junction.veh_set & junction.observed_veh_set:
                junction.update_phase_time_loss_list_by_veh(veh)

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

    def report(self, log_filename: str):
        report = {'trip_avg': self.calc_trips_statistics()}
        self.calc_loss()

        log = {}
        for junction in self.junction_list:
            junction_name = junction.junction_name
            report[junction_name] = {
                'penetration_rate': self.penetration_rate,
                'total_time_loss': self.total_loss_by_junction_name[junction_name],
                'duration_by_phase': junction.duration_by_phase,
                'weight_by_phase': junction.weight_by_phase
            }
            log[junction_name] = {
                'phase_start_t': junction.phase_log[0],
                'phase': junction.phase_log[1]
            }

        with open(self.report_filename, 'w') as data_file:
            json.dump(report, data_file, indent=2)
        with open(log_filename, 'w') as data_file:
            json.dump(log, data_file, indent=2)
        return report


class SimFixed(SimBase):
    def __init__(self, junction_list: List[JunctionFixed],
                 cmd: List[str],
                 detector_output_file: str,
                 trip_output_filename: str,
                 report_filename: str,
                 net_filename: str):
        super().__init__(junction_list, detector_output_file, trip_output_filename, report_filename)
        self.net_filename = net_filename
        self.setting_fixed_timing()
        traci.start(cmd)

    def setting_fixed_timing(self):
        green_by_phase_by_junction_id = {}
        for junction in self.junction_list:
            green_by_phase_by_junction_id[junction.junction_id] = junction.green_by_phase

        tree = et.parse(self.net_filename)
        root = tree.getroot()

        for signal_light_info in root.findall('tlLogic'):
            junction_id = signal_light_info.get('id')
            if junction_id not in green_by_phase_by_junction_id:
                continue
            green_by_phase = green_by_phase_by_junction_id[junction_id]
            for idx, phase_info in enumerate(signal_light_info):
                if idx % 3 == 0:
                    phase = f'{idx // 3 + 1}'
                    green = f'{green_by_phase[phase]}'
                    phase_info.set('duration', green)
        tree.write(self.net_filename)

    def control(self):
        while self.has_veh():
            self.run()

    def report(self):
        report = {'trip_avg': self.calc_trips_statistics()}
        self.calc_loss()
        for junction in self.junction_list:
            junction_name = junction.junction_name
            report[junction_name] = {
                'total_time_loss': self.total_loss_by_junction_name[junction_name],
                'effective_green': junction.effective_green,
                'green_by_phase': junction.green_by_phase
            }

        with open(self.report_filename, 'w') as data_file:
            json.dump(report, data_file, indent=2)

        return report


class SimAdaptive(SimBase):
    def __init__(self, junction_list: List[JunctionAdaptive],
                 cmd: List[str],
                 detector_output_file: str,
                 trip_output_filename: str,
                 report_filename: str,
                 penetration_rate: float = 1.0):
        super().__init__(junction_list, detector_output_file, trip_output_filename, report_filename)
        traci.start(cmd)
        self.penetration_rate = penetration_rate
        self.observed_veh_set = set()
        self.veh_num_list = []

    def collect_veh_data(self):
        veh_list = traci.vehicle.getIDList()
        for veh in veh_list:
            lane_id = traci.vehicle.getLaneID(veh)
            if not lane_id:
                continue
            route = traci.vehicle.getRouteID(veh).split('_')[1]
            edge_id = lane_id.split('_')[0]
            junction: JunctionAdaptive | None = None
            for _junction in self.junction_list:
                if route not in _junction.route_set:
                    continue
                if edge_id in _junction.edge_list:
                    junction = _junction
                    junction.route_by_veh[veh] = route
                    break
            if junction is None:
                continue
            is_stop = bool(traci.vehicle.getWaitingTime(veh))
            stop_delay = traci.vehicle.getAccumulatedWaitingTime(veh)
            if veh not in junction.veh_set:
                junction.init_stop_num_by_veh[veh] = int(is_stop)
                junction.accumulate_stop_num_by_veh[veh] = int(is_stop)
                junction.veh_state_by_veh[veh] = is_stop
                junction.init_stop_delay_by_veh[veh] = stop_delay
                junction.veh_set.add(veh)
                if random.random() >= 1 - self.penetration_rate:
                    junction.observed_veh_set.add(veh)
            if is_stop != junction.veh_state_by_veh[veh] and is_stop:
                junction.accumulate_stop_num_by_veh[veh] += 1
            junction.veh_state_by_veh[veh] = is_stop
            junction.accumulate_stop_delay_by_veh[veh] = stop_delay

    def control(self):
        while self.has_veh():
            self.run()
            if self.get_current_ts() % 120 == 0:
                self.veh_num_list.append(traci.vehicle.getIDCount())
            self.collect_veh_data()

            for junction in self.junction_list:
                junction.count_down()
                if junction.at_the_end_of_cycle:
                    junction.calc_new_green_time()
                    keep_veh_list = []
                    for veh in junction.veh_set:
                        try:
                            lane_id = traci.vehicle.getLaneID(veh) or 'None'
                        except:
                            lane_id = 'None'
                        edge_id = lane_id.split('_')[0]
                        if edge_id in junction.edge_list:
                            keep_veh_list.append(veh)
                        # Clean passed vehicles
                        else:
                            del junction.veh_state_by_veh[veh]
                            del junction.init_stop_delay_by_veh[veh]
                            del junction.accumulate_stop_delay_by_veh[veh]
                            del junction.init_stop_num_by_veh[veh]
                            del junction.accumulate_stop_num_by_veh[veh]
                            del junction.route_by_veh[veh]
                            if veh in junction.observed_veh_set:
                                junction.observed_veh_set.remove(veh)
                    junction.veh_set = set(keep_veh_list)

    def report(self, log_filename: str):
        report = {'trip_avg': self.calc_trips_statistics(),'veh_num_list': self.veh_num_list}
        self.calc_loss()
        log = {}
        for junction in self.junction_list:
            junction_name = junction.junction_name
            report[junction_name] = {
                'penetration_rate': self.penetration_rate,
                'total_time_loss': self.total_loss_by_junction_name[junction_name]
            }
            log[junction_name] = {
                'phase_start_t': junction.phase_log[0],
                'phase': junction.phase_log[1]
            }

        with open(self.report_filename, 'w') as data_file:
            json.dump(report, data_file, indent=2)
        with open(log_filename, 'w') as data_file:
            json.dump(log, data_file, indent=2)
        return report
