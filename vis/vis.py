import os
import configparser
import sys
import glob
import csv
import pprint
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from  matplotlib.ticker import FuncFormatter

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__),'..','scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA = os.path.join(BASE_PATH, '..', 'results')
DATA_OUTPUT = os.path.join(BASE_PATH, '..', 'vis', 'outputs')


if not os.path.exists(DATA_OUTPUT):
    os.mkdir(DATA_OUTPUT)


def load_in_all_main_lut(max_isd_distance):

    filenames = glob.iglob(os.path.join(DATA, 'full_tables', 'full_capacity*'))

    output = pd.concat((pd.read_csv(f) for f in filenames))

    output['capacity_per_Hz_km2'] = (
        output['capacity_mbps_km2'] / (output['bandwidth_MHz'] * 1e6)
        )

    output['sites_per_km2'] = output.sites_per_km2.round(1)

    output['inter_site_distance_km'] = output['inter_site_distance_m'] / 1e3

    output = output.replace(
        {
            'environment':{
                'urban': 'Urban',
                'suburban': 'Suburban',
                'rural': 'Rural',
            }
        }
    )

    output = output.reset_index().reset_index(drop=True)

    ISD = output.inter_site_distance_km.astype(int) < max_isd_distance
    output = output[ISD]

    return output


def plotting_function1_isd(data):

    data_subset = data[['inter_site_distance_km','frequency_GHz','path_loss_dB',
    'received_power_dB', 'interference_dB', 'sinr_dB', 'spectral_efficiency_bps_hz',
    'capacity_mbps_km2']]

    data_subset.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Path Loss',
        'Received Power', 'Interference', 'SINR', 'SE',
        'Channel Capacity']

    long_data = pd.melt(data_subset,
        id_vars=['Inter-Site Distance (km)', 'Frequency (GHz)'],
        value_vars=['Path Loss', 'Received Power', 'Interference',
            'SINR', 'SE', 'Channel Capacity'])

    long_data.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)',
        'Metric', 'Value']

    sns.set(font_scale=1.1)

    plot = sns.relplot(x="Inter-Site Distance (km)", y='Value', hue="Frequency (GHz)",
        col="Metric", col_wrap=2, palette=sns.color_palette("husl", 6),
        kind="line", data=long_data,
        facet_kws=dict(sharex=False, sharey=False),
        legend="full")

    handles = plot._legend_data.values()
    labels = plot._legend_data.keys()
    plot._legend.remove()
    plot.fig.legend(handles=handles, labels=labels, loc='lower center', ncol=7)

    plot.axes[0].set_ylabel('Path Loss (dB)')
    plot.axes[1].set_ylabel('Received Power (dBm)')
    plot.axes[2].set_ylabel('Interference (dBm)')
    plot.axes[3].set_ylabel('SINR (dB)')
    plot.axes[4].set_ylabel('SE (Bps/Hz)')
    plot.axes[5].set_ylabel('Capacity (Mbps km^2)')

    plot.axes[0].set_xlabel('Inter-Site Distance (km)')
    plot.axes[1].set_xlabel('Inter-Site Distance (km)')
    plot.axes[2].set_xlabel('Inter-Site Distance (km)')
    plot.axes[3].set_xlabel('Inter-Site Distance (km)')
    plot.axes[4].set_xlabel('Inter-Site Distance (km)')
    plot.axes[5].set_xlabel('Inter-Site Distance (km)')

    plt.subplots_adjust(hspace=0.3, wspace=0.3, bottom=0.07)

    plot.savefig(DATA_OUTPUT + '/frequency_capacity_barplot_isd.png', dpi=300)

    return print('completed (frequency) barplot (isd)')


def load_summary_lut(max_isd_distance):

    filename = os.path.join(DATA, 'percentile_50_capacity_lut.csv')

    output = pd.read_csv(filename)

    output['sites_per_km2'] = output.sites_per_km2.round(4)

    output['inter_site_distance_km'] = output['inter_site_distance_m'] / 1e3

    output = output.loc[output['environment'] == 'suburban']

    output = output[['inter_site_distance_km',
        'strategy',
        'ran_sector_antenna_costs_km2',
        'ran_remote_radio_unit_costs_km2',
        'ran_baseband_unit_costs_km2',
        'site_rental_km2',
        'civil_tower_costs_km2',
        'civil_material_costs_km2',
        'civil_transportation_costs_km2',
        'civil_installation_costs_km2',
        'power_system_costs_km2',
        'backhaul_fiber_backhaul_costs_km2',
        'backhaul_router_costs_km2'
    ]]

    output['results type'] = 'Raw ($/km2)'

    output = output.reset_index().reset_index(drop=True)

    ISD = output.inter_site_distance_km.astype(int) < max_isd_distance
    output = output[ISD]

    return output


def generate_long_data(data):

    subset = data[[
        'inter_site_distance_km',
        'strategy',
        'results type',
        'ran_sector_antenna_costs_km2',
        'ran_remote_radio_unit_costs_km2',
        'ran_baseband_unit_costs_km2',
        'site_rental_km2',
        'civil_tower_costs_km2',
        'civil_material_costs_km2',
        'civil_transportation_costs_km2',
        'civil_installation_costs_km2',
        'power_system_costs_km2',
        'backhaul_fiber_backhaul_costs_km2',
        'backhaul_router_costs_km2'
    ]]

    subset.columns = [
        'ISD (km)', 'Strategy', 'Results Type',
        'RAN Antenna', 'RAN RRU', 'RAN BBU',
        'Site Rental', 'Civil Tower', 'Civil Material', 'Civil Transport',
        'Civil Installation', 'Power System', 'Backhaul Fiber', 'Backhaul Router'
    ]

    list_of_dicts = subset.to_dict('records')

    intermediate = []

    for item in list_of_dicts:
        intermediate.append(item)
        total_cost = 0
        for key, value in item.items():
            if key == 'ISD (km)' or key == 'Strategy' or key == 'Results Type':
                pass
            else:
                total_cost += value

        intermediate.append({
                'Results Type': 'Percentage (%)',
                'Strategy': item['Strategy'],
                'ISD (km)': item['ISD (km)'],
                'RAN Antenna': round(item['RAN Antenna'] / total_cost * 100,2),
                'RAN RRU': round(item['RAN RRU'] / total_cost * 100, 2),
                'RAN BBU': round(item['RAN BBU'] / total_cost * 100, 2),
                'Site Rental': round(item['Site Rental'] / total_cost * 100, 2),
                'Civil Tower': round(item['Civil Tower'] / total_cost * 100, 2),
                'Civil Material': round(item['Civil Material'] / total_cost * 100, 2),
                'Civil Transport': round(item['Civil Transport'] / total_cost * 100, 2),
                'Civil Installation': round(item['Civil Installation'] / total_cost * 100, 2),
                'Power System': round(item['Power System'] / total_cost * 100, 2),
                'Backhaul Fiber': round(item['Backhaul Fiber'] / total_cost * 100, 2),
                'Backhaul Router': round(item['Backhaul Router'] / total_cost * 100, 2),
                'Total': 100,
        })

    all_data = pd.DataFrame(intermediate)

    output = pd.melt(all_data,
        id_vars=['ISD (km)', 'Strategy', 'Results Type',
        ],
        value_vars=[
            'RAN Antenna', 'RAN RRU', 'RAN BBU', 'Site Rental', 'Civil Tower',
            'Civil Material', 'Civil Transport', 'Civil Installation', 'Power System',
            'Backhaul Fiber', 'Backhaul Router',
        ])

    output.columns = ['ISD', 'Strategy', 'Results Type', 'Component', 'gross_value']

    output['Cost'] = round(output['gross_value'] / 1000)

    output = output[['ISD', 'Strategy', 'Component', 'Cost']]

    output['Metric'] = output['Component'].str.split(" ", n = 1, expand = True)[0]

    output = output.replace(
        {
            'Metric':{
                'ran': 'RAN',
                'site': 'Site',
                'civil': 'Civil works',
                'power': 'Power',
                'backhaul': 'Backhaul',
            }
        }
    )

    output = output.replace(
        {
            'Strategy':{
                'baseline': 'Baseline (No Sharing)',
                'passive_site_sharing': 'Passive Site Sharing',
                'passive_backhaul_sharing': 'Passive Backhaul Sharing',
                'active_moran': 'Multi-Operator RAN',
            }
        }
    )

    return output


def calculate_strategy_results(data):

    data = data.replace(
        {
            'strategy':{
                'baseline': 'Baseline (No Sharing)',
                'passive_site_sharing': 'Passive Site Sharing',
                'passive_backhaul_sharing': 'Passive Backhaul Sharing',
                'active_moran': 'Multi Operator RAN',
            }
        }
    )

    subset = data[[
        'inter_site_distance_km',
        'strategy',
        'ran_sector_antenna_costs_km2',
        'ran_remote_radio_unit_costs_km2',
        'ran_baseband_unit_costs_km2',
        'site_rental_km2',
        'civil_tower_costs_km2',
        'civil_material_costs_km2',
        'civil_transportation_costs_km2',
        'civil_installation_costs_km2',
        'power_system_costs_km2',
        'backhaul_fiber_backhaul_costs_km2',
        'backhaul_router_costs_km2'
    ]]

    bins = [
        (0.5, 1.5),
        (1.5, 2.5),
        (2.5, 3.5),
        (3.5, 4.5),
        (4.5, 5.5),
    ]

    strategies = [
        'Baseline (No Sharing)',
        'Passive Site Sharing',
        'Passive Backhaul Sharing',
        'Multi Operator RAN',
    ]

    intermediate = []

    ran_sector_antenna_costs_km2 = []
    ran_remote_radio_unit_costs_km2 = []
    ran_baseband_unit_costs_km2 = []
    site_rental_km2 = []
    civil_tower_costs_km2 = []
    civil_material_costs_km2 = []
    civil_transportation_costs_km2 = []
    civil_installation_costs_km2 = []
    power_system_costs_km2 = []
    backhaul_fiber_backhaul_costs_km2 = []
    backhaul_router_costs_km2 = []
    # total_cost_km2 = []

    for strategy in strategies:
        for lower, upper in bins:
            for item in subset.to_dict('records'):
                if item['strategy'] == strategy:
                    if lower <= item['inter_site_distance_km'] < upper:

                        ran_sector_antenna_costs_km2.append(item['ran_sector_antenna_costs_km2'])
                        ran_remote_radio_unit_costs_km2.append(item['ran_remote_radio_unit_costs_km2'])
                        ran_baseband_unit_costs_km2.append(item['ran_baseband_unit_costs_km2'])
                        site_rental_km2.append(item['site_rental_km2'])
                        civil_tower_costs_km2.append(item['civil_tower_costs_km2'])
                        civil_material_costs_km2.append(item['civil_material_costs_km2'])
                        civil_transportation_costs_km2.append(item['civil_transportation_costs_km2'])
                        civil_installation_costs_km2.append(item['civil_installation_costs_km2'])
                        power_system_costs_km2.append(item['power_system_costs_km2'])
                        backhaul_fiber_backhaul_costs_km2.append(item['backhaul_fiber_backhaul_costs_km2'])
                        backhaul_router_costs_km2.append(item['backhaul_router_costs_km2'])


            intermediate.append({
                'Results Type': 'Raw ($/km2)',
                'Strategy': strategy,
                'ISD (km)': (lower + upper) / 2,
                'RAN Antenna': sum(ran_sector_antenna_costs_km2) / len(ran_sector_antenna_costs_km2),
                'RAN RRU': sum(ran_remote_radio_unit_costs_km2) / len(ran_remote_radio_unit_costs_km2),
                'RAN BBU': sum(ran_baseband_unit_costs_km2) / len(ran_baseband_unit_costs_km2),
                'Site Rental': sum(site_rental_km2) / len(site_rental_km2),
                'Civil Tower': sum(civil_tower_costs_km2) / len(civil_tower_costs_km2),
                'Civil Material': sum(civil_material_costs_km2) / len(civil_material_costs_km2),
                'Civil Transport': sum(civil_transportation_costs_km2) / len(civil_transportation_costs_km2),
                'Civil Installation': sum(civil_installation_costs_km2) / len(civil_installation_costs_km2),
                'Power System': sum(power_system_costs_km2) / len(power_system_costs_km2),
                'Backhaul Fiber': sum(backhaul_fiber_backhaul_costs_km2) / len(backhaul_fiber_backhaul_costs_km2),
                'Backhaul Router': sum(backhaul_router_costs_km2) / len(backhaul_router_costs_km2),
                # 'Total': sum(total_cost_km2) / len(total_cost_km2),
            })

    output = []

    for item in intermediate:
        output.append(item)
        total_cost = 0
        for key, value in item.items():
            if key == 'ISD (km)' or key == 'Strategy' or key == 'Results Type':
                pass
            else:
                total_cost += value

        output.append({
                'Results Type': 'Percentage (%)',
                'Strategy': item['Strategy'],
                'ISD (km)': item['ISD (km)'],
                'RAN Antenna': round(item['RAN Antenna'] / total_cost * 100,2),
                'RAN RRU': round(item['RAN RRU'] / total_cost * 100, 2),
                'RAN BBU': round(item['RAN BBU'] / total_cost * 100, 2),
                'Site Rental': round(item['Site Rental'] / total_cost * 100, 2),
                'Civil Tower': round(item['Civil Tower'] / total_cost * 100, 2),
                'Civil Material': round(item['Civil Material'] / total_cost * 100, 2),
                'Civil Transport': round(item['Civil Transport'] / total_cost * 100, 2),
                'Civil Installation': round(item['Civil Installation'] / total_cost * 100, 2),
                'Power System': round(item['Power System'] / total_cost * 100, 2),
                'Backhaul Fiber': round(item['Backhaul Fiber'] / total_cost * 100, 2),
                'Backhaul Router': round(item['Backhaul Router'] / total_cost * 100, 2),
                # 'Total': 100,
        })

    return output


def plotting_function2(data):

    data['ISD'] = round(data['ISD'], 3)

    bins = [0, 1, 2, 3, 4, 5]
    data['ISD_binned'] = pd.cut(data['ISD'], bins, labels=["1", "2", "3", "4", "5"])

    plot = sns.catplot(x='ISD_binned', y='Cost',
        hue="Metric",
        col="Strategy", col_wrap=2,
        kind='bar',
        data=data,
        palette=sns.color_palette("husl", 10),
        sharex=True,
        sharey=True,
        legend="full"
        )

    handles = plot._legend_data.values()
    labels = plot._legend_data.keys()
    plot._legend.remove()
    plot.fig.legend(handles=handles, labels=labels,
        loc='lower center', ncol=6)

    plot.axes[0].set_ylabel('Cost (USD$k km^2)')
    plot.axes[1].set_ylabel('Cost (USD$k km^2)')
    plot.axes[2].set_ylabel('Cost (USD$k km^2)')
    plot.axes[3].set_ylabel('Cost (USD$k km^2)')

    plot.axes[0].set_xlabel('ISD (km)')
    plot.axes[1].set_xlabel('ISD (km)')
    plot.axes[2].set_xlabel('ISD (km)')
    plot.axes[3].set_xlabel('ISD (km)')

    plt.subplots_adjust(hspace=0.2, wspace=0.1, bottom=0.1)

    plot.savefig(DATA_OUTPUT + '/costs_capacity_barplot_isd_density.png', dpi=300)

    return print('completed (capacity-cost) replot (isd)')


def mean_summarized_cost_results(data):

    unique_isd = set()
    unique_strategies = set()
    cost_saving_by_strategy = []
    summarized_data = []

    for item in data:
        ran_cost = 0
        site_rental = 0
        civils_cost = 0
        power_cost = 0
        backhaul_cost = 0
        total_cost = 0

        for key, value in item.items():
            if key == 'ISD (km)':
                unique_isd.add(value)
            if key == 'Strategy':
                unique_strategies.add(value)
            if key == 'ISD (km)' or key == 'Strategy' or key == 'Results Type':
                pass
            else:
                cost_type = key.split(' ')[0]

                total_cost += value

                if cost_type == 'RAN':
                    ran_cost += value
                elif cost_type == 'Site':
                    site_rental += value
                elif cost_type == 'Civil':
                    civils_cost += value
                elif cost_type == 'Power':
                    power_cost += value
                elif cost_type == 'Backhaul':
                    backhaul_cost += value

        if item['Results Type'] == 'Raw ($/km2)':
            cost_saving_by_strategy.append({
                'Strategy': item['Strategy'],
                'ISD (km)': item['ISD (km)'],
                'total_cost': total_cost,
            })

        summarized_data.append({
            'Results Type': item['Results Type'],
            'Strategy': item['Strategy'],
            'ISD (km)': item['ISD (km)'],
            'RAN': ran_cost,
            'Site Rental': site_rental,
            'Civil': civils_cost,
            'Power': power_cost,
            'Backhaul': backhaul_cost,
        })

    strategy_savings = []
    for strategy in list(unique_strategies):
        for isd in list(unique_isd):
            for item in cost_saving_by_strategy:
                if item['Strategy'] == 'Baseline (No Sharing)' and item['ISD (km)'] == isd:
                    baseline_total_cost = item['total_cost']
            for item in cost_saving_by_strategy:
                if not strategy == 'Baseline (No Sharing)' and item['ISD (km)'] == isd:
                    total_cost = item['total_cost']
            strategy_savings.append({
                'Strategy': strategy,
                'ISD (km)': isd,
                'Saving (%)': round(total_cost / baseline_total_cost * 100, 1),
            })

    return summarized_data, strategy_savings


def csv_writer(data, directory, filename):
    """
    Write data to a CSV file path
    """
    # Create path
    if not os.path.exists(directory):
        os.makedirs(directory)

    fieldnames = []
    for name, value in data[0].items():
        fieldnames.append(name)

    with open(os.path.join(directory, filename), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, lineterminator = '\n')
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':

    max_isd_distance = 5

    data = load_in_all_main_lut(max_isd_distance)

    # plotting_function1_isd(data)

    wide_data = load_summary_lut(max_isd_distance)

    # long_data = generate_long_data(wide_data)

    # plotting_function2(long_data)

    mean_results = calculate_strategy_results(wide_data)

    # csv_writer(mean_results, DATA_OUTPUT, 'mean_item_cost_results.csv')

    mean_summarized_results, strategy_savings = mean_summarized_cost_results(mean_results)

    csv_writer(mean_summarized_results, DATA_OUTPUT, 'mean_summarized_cost_results.csv')

    csv_writer(strategy_savings, DATA_OUTPUT, 'mean_strategy_savings.csv')

    # pprint.pprint(strategy_savings)
