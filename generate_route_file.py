# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

label_size = 16
mpl.rcParams['xtick.labelsize'] = label_size
mpl.rcParams['ytick.labelsize'] = label_size


def main():
    file_template = '''<?xml version="1.0" encoding="UTF-8"?>

    <!-- generated on 2022-10-27 22:22:12 by Eclipse SUMO netedit Version 1.14.1
    -->

    <routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">
        <!-- Routes -->
        <route id="r_1" edges="441190721#0 142178743#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411670856#0 441386534"/>
        <route id="r_2" edges="441190721#0 142178743#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411653583#0 441386541#0"/>
        <route id="r_3" edges="441190721#0 142178743#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 -411728065#1"/>
        <route id="r_4" edges="441190721#0 142178743#0 478958406#0"/>
        <route id="r_5" edges="441190721#0 142178743#0 -412646493#2 -897491920#2"/>
        <route id="r_6" edges="411705024 -412646493#2 -897491920#2"/>
        <route id="r_7" edges="411705024 -142178743#2 -441190721#3"/>
        <route id="r_8" edges="411705024 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411670856#0"/>
        <route id="r_9" edges="411705024 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411653583#0 441386541#0"/>
        <route id="r_10" edges="411705024 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 -411728065#1"/>
        <route id="r_11" edges="897491918 412646493#0 -142178743#2 -441190721#3"/>
        <route id="r_12" edges="897491918 412646493#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411670856#0"/>
        <route id="r_13" edges="897491918 412646493#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411653583#0 441386541#0"/>
        <route id="r_14" edges="897491918 412646493#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 -411728065#1"/>
        <route id="r_15" edges="897491918 412646493#0 478958406#0"/>
        <route id="r_16" edges="-441386533#5 -411670856#1 411653583#0 441386541#0"/>
        <route id="r_17" edges="-441386533#5 -411670856#1 -411728065#1"/>
        <route id="r_18" edges="-441386533#5 -411670856#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 478958406#0"/>
        <route id="r_19" edges="-441386533#5 -411670856#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -412646493#2 -897491920#2"/>
        <route id="r_20" edges="-441386533#5 -411670856#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -142178743#2 -441190721#3"/>
        <route id="r_21" edges="411728065#0 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 478958406#0"/>
        <route id="r_22" edges="411728065#0 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -412646493#2 -897491920#2"/>
        <route id="r_23" edges="411728065#0 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -142178743#2 -441190721#3"/>
        <route id="r_24" edges="411728065#0 411670856#0 441386534"/>
        <route id="r_25" edges="411728065#0 411653583#0 441386541#0"/>
        <route id="r_26" edges="-897491917#1 -411653583#1 -411728065#1"/>
        <route id="r_27" edges="-897491917#1 -411653583#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 478958406#0"/>
        <route id="r_28" edges="-897491917#1 -411653583#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -412646493#2 -897491920#2"/>
        <route id="r_29" edges="-897491917#1 -411653583#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -142178743#2 -441190721#3"/>
        <route id="r_30" edges="-897491917#1 -411653583#1 411670856#0 441386534"/>

        <!-- Vehicles -->
        {}
    </routes>'''
    original_probability = {
        1: 0.002663889,
        2: 0.048272222,
        3: 0.002397222,
        4: 0.063,
        5: 0.0036,
        6: 0.069766667,
        7: 0.085463889,
        8: 0.004697222,
        9: 0.085105556,
        10: 0.004227778,
        11: 0.003388889,
        12: 0.011469444,
        13: 0.207827778,
        14: 0.010322222,
        15: 0.049719444,
        16: 0.15215,
        17: 0.031875,
        18: 0.005341667,
        19: 0.020094444,
        20: 0.002825,
        21: 0.008294444,
        22: 0.0312,
        23: 0.004388889,
        24: 0.048930556,
        25: 0.101355556,
        26: 0.021005556,
        27: 0.041316667,
        28: 0.155433333,
        29: 0.021861111,
        30: 0.119191667
    }

    edge_by_route = {
        1: "441190721#0 142178743#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411670856#0 441386534",
        2: "441190721#0 142178743#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411653583#0 441386541#0",
        3: "441190721#0 142178743#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 -411728065#1",
        4: "441190721#0 142178743#0 478958406#0",
        5: "441190721#0 142178743#0 -412646493#2 -897491920#2",
        6: "411705024 -412646493#2 -897491920#2",
        7: "411705024 -142178743#2 -441190721#3",
        8: "411705024 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411670856#0",
        9: "411705024 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411653583#0 441386541#0",
        10: "411705024 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 -411728065#1",
        11: "897491918 412646493#0 -142178743#2 -441190721#3",
        12: "897491918 412646493#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411670856#0",
        13: "897491918 412646493#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 411653583#0 441386541#0",
        14: "897491918 412646493#0 222786843#0 441190750#3 553146929#0 553146928#0 411672987#0 -411728065#1",
        15: "897491918 412646493#0 478958406#0",
        16: "-441386533#5 -411670856#1 411653583#0 441386541#0",
        17: "-441386533#5 -411670856#1 -411728065#1",
        18: "-441386533#5 -411670856#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 478958406#0",
        19: "-441386533#5 -411670856#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -412646493#2 -897491920#2",
        20: "-441386533#5 -411670856#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -142178743#2 -441190721#3",
        21: "411728065#0 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 478958406#0",
        22: "411728065#0 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -412646493#2 -897491920#2",
        23: "411728065#0 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -142178743#2 -441190721#3",
        24: "411728065#0 411670856#0 441386534",
        25: "411728065#0 411653583#0 441386541#0",
        26: "-897491917#1 -411653583#1 -411728065#1",
        27: "-897491917#1 -411653583#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 478958406#0",
        28: "-897491917#1 -411653583#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -412646493#2 -897491920#2",
        29: "-897491917#1 -411653583#1 -411672987#1 -441386542 -553146929#4 -441190750#5 -441190750#2 -441190750#2.108 -142178743#2 -441190721#3",
        30: "-897491917#1 -411653583#1 411670856#0 441386534"
    }

    original_vph = {
        1: 9.59,
        2: 173.78,
        3: 8.63,
        4: 226.8,
        5: 12.96,
        6: 251.16,
        7: 307.67,
        8: 16.91,
        9: 306.38,
        10: 15.22,
        11: 12.2,
        12: 41.29,
        13: 748.18,
        14: 37.16,
        15: 178.99,
        16: 547.74,
        17: 114.75,
        18: 19.23,
        19: 72.34,
        20: 10.17,
        21: 29.86,
        22: 112.32,
        23: 15.8,
        24: 176.15,
        25: 364.88,
        26: 75.62,
        27: 148.74,
        28: 559.56,
        29: 78.7,
        30: 429.09
    }

    def independent_route_files():
        line_template_poisson = '<flow id="v_{}" type="DEFAULT_VEHTYPE" route="r_{}" begin="0" end="{}" period="exp({:.8f})"/>'

        one_experiment_time = 4 * 3600
        experiment_num = 8

        np.random.seed(0)

        fluctuated_prob_np_by_route = {}
        for route, org_prob in original_probability.items():
            x = np.random.rand() * np.pi
            x_list = []
            for i in range(experiment_num):
                x_list.append((x + i * np.pi / experiment_num) % np.pi)
            fluctuated_prob_np = np.sin(x_list) * np.pi / 2 * org_prob
            fluctuated_prob_np_by_route[route] = fluctuated_prob_np
        for i in range(experiment_num):
            line_list = []
            for route, fluctuated_prob_np in fluctuated_prob_np_by_route.items():
                line_list.append(line_template_poisson.format(route,
                                                              route,
                                                              one_experiment_time,
                                                              fluctuated_prob_np[i]))
            with open(f'sumo_files/osm_{i + 1}.rou.xml', 'w') as data_file:
                data_file.write(file_template.format('\n'.join(line_list)))

    def different_period_in_one_route():
        # file_template = '<flows>{}</flows>'
        one_period_time = 1800
        period_num = 8

        line_template_vph = '<flow id="v_{}_{}" type="DEFAULT_VEHTYPE" route="r_{}" begin="{}" end="{}" vehsPerHour="{:.2f}"/>'

        np.random.seed(4)
        x = np.random.rand() * np.pi
        x_list = []
        for i in range(period_num):
            x_list.append((x + i * np.pi / period_num) % np.pi)
        fluctuated_coef_np = (np.sin(x_list) - np.pi / 2 + 1) * 0.65 + 1

        line_list = []
        for i in range(period_num):
            for route, org_vph in original_vph.items():
                line_list.append(line_template_vph.format(route, i + 1,
                                                          route,
                                                          i * one_period_time, (i + 1) * one_period_time,
                                                          fluctuated_coef_np[i] * org_vph))
        with open(f'sumo_files/osm_duarouter.rou.xml', 'w') as data_file:
            data_file.write(file_template.format('\n        '.join(line_list)))

        x = []
        y = []
        for i, [t0, t1] in enumerate(zip(range(period_num), range(1, period_num + 1))):
            x.extend([t0 * 1800, t1 * 1800])
            y.extend([fluctuated_coef_np[i], fluctuated_coef_np[i]])
        plt.figure(figsize=(8, 6))
        plt.plot(x, y)
        plt.xlabel('time in simulation (s)', fontsize=20)
        plt.ylabel('coefficient of the average volume', fontsize=20)
        plt.tight_layout()
        # plt.show()
        print(np.mean(fluctuated_coef_np))
        plt.savefig(f'figures/sim_volume_profile.png', dpi=200)

    different_period_in_one_route()


if __name__ == '__main__':
    main()
