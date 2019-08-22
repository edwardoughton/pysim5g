import os
import configparser
import sys
import glob
import csv
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
DATA_OUTPUT = os.path.join(BASE_PATH, '..', 'vis', 'figures')


if not os.path.exists(DATA_OUTPUT):
    os.mkdir(DATA_OUTPUT)


def load_in_all_main_lut():

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

    return output


def plotting_function1(data):

    data_subset = data[['sites_per_km2','frequency_GHz','path_loss_dB', 'received_power_dB',
    'interference_dB', 'sinr_dB', 'spectral_efficiency_bps_hz', 'capacity_mbps_km2']]

    data_subset.columns = ['Density (km^2)', 'Frequency (GHz)', 'Path Loss',
        'Received Power', 'Interference', 'SINR', 'SE',
        'Channel Capacity']

    long_data = pd.melt(data_subset,
        id_vars=['Density (km^2)', 'Frequency (GHz)'],
        value_vars=['Path Loss', 'Received Power', 'Interference', 'SINR', 'SE',
        'Channel Capacity'])

    long_data.columns = ['Density (km^2)', 'Frequency (GHz)', 'Metric', 'Value']

    long_data['Frequency (GHz)'] = long_data['Frequency (GHz)'].astype(str) + 'GHz'

    sns.set(font_scale=1.1)

    plot = sns.catplot(x='Density (km^2)', y='Value', hue="Frequency (GHz)", kind="bar",
        col="Metric", col_wrap=2, data=long_data, palette=sns.color_palette("husl", 5),
        sharey=False, sharex=False, legend="full")

    handles = plot._legend_data.values()
    labels = plot._legend_data.keys()
    plot._legend.remove()
    plot.fig.legend(handles=handles, labels=labels, loc='lower center', ncol=5)

    plot.axes[0].set_ylabel('Path Loss (dB)')
    plot.axes[1].set_ylabel('Received Power (dBm)')
    plot.axes[2].set_ylabel('Interference (dBm)')
    plot.axes[3].set_ylabel('SINR (dB)')
    plot.axes[4].set_ylabel('SE (Bps/Hz)')
    plot.axes[5].set_ylabel('Capacity (Mbps/km^2)')

    plot.axes[0].set_xlabel('Site Density (km^2)')
    plot.axes[1].set_xlabel('Site Density (km^2)')
    plot.axes[2].set_xlabel('Site Density (km^2)')
    plot.axes[3].set_xlabel('Site Density (km^2)')
    plot.axes[4].set_xlabel('Site Density (km^2)')
    plot.axes[5].set_xlabel('Site Density (km^2)')

    plt.subplots_adjust(hspace=0.3, wspace=0.3, bottom=0.07)

    plot.savefig(DATA_OUTPUT + '/frequency_capacity_barplot_area.png')

    return print('completed (frequency) barplot (area)')


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
        col="Metric", col_wrap=2, palette=sns.color_palette("husl", 5),
        kind="line", data=long_data,
        facet_kws=dict(sharex=False, sharey=False),
        legend="full")

    handles = plot._legend_data.values()
    labels = plot._legend_data.keys()
    plot._legend.remove()
    plot.fig.legend(handles=handles, labels=labels, loc='lower center', ncol=6)

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

    plot.savefig(DATA_OUTPUT + '/frequency_capacity_barplot_isd.png')

    return print('completed (frequency) barplot (isd)')


def plotting_function2(data):

    data_subset = data[['inter_site_distance_km','frequency_GHz','path_loss_dB',
        'received_power_dB', 'interference_dB', 'sinr_dB', 'spectral_efficiency_bps_hz',
        'capacity_mbps_km2', 'environment']]

    data_subset.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Path Loss',
        'Received Power', 'Interference', 'SINR', 'SE', 'Channel Capacity','Environment']

    long_data = pd.melt(data_subset,
        id_vars=['Inter-Site Distance (km)', 'Frequency (GHz)', 'Environment'],
        value_vars=['Path Loss',
        'Received Power', 'Interference', 'SINR', 'SE', 'Channel Capacity'])

    long_data.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)',
    'Environment', 'Metric', 'Value']

    plot = sns.relplot(x="Inter-Site Distance (km)", y='Value', hue="Environment",
        col="Metric", col_wrap=2,
        kind="line", data=long_data, palette=sns.color_palette("husl", 3),
        facet_kws=dict(sharex=False, sharey=False), hue_order=["Urban", "Suburban", "Rural"],
        legend="full")

    handles = plot._legend_data.values()
    labels = plot._legend_data.keys()
    plot._legend.remove()
    plot.fig.legend(handles=handles, labels=labels, loc='lower center', ncol=4)

    plot.axes[0].set_ylabel('Path Loss (dB)')
    plot.axes[1].set_ylabel('Received Power (dBm)')
    plot.axes[2].set_ylabel('Interference (dBm)')
    plot.axes[3].set_ylabel('SINR (dB)')
    plot.axes[4].set_ylabel('SE (Bps/Hz)')
    plot.axes[5].set_ylabel('Channel Capacity (Mbps km^2)')

    plot.axes[0].set_xlabel('Inter-Site Distance (km)')
    plot.axes[1].set_xlabel('Inter-Site Distance (km)')
    plot.axes[2].set_xlabel('Inter-Site Distance (km)')
    plot.axes[3].set_xlabel('Inter-Site Distance (km)')
    plot.axes[4].set_xlabel('Inter-Site Distance (km)')
    plot.axes[5].set_xlabel('Inter-Site Distance (km)')

    plt.subplots_adjust(hspace=0.3, wspace=0.3, bottom=0.07)

    plot.savefig(DATA_OUTPUT + '/urban_rural_capacity_lineplot.png')

    return print('completed (urban-rural) replot (isd)')


def load_summary_lut(max_isd_distance):

    filename = os.path.join(DATA, 'percentile_50_capacity_lut.csv')

    output = pd.read_csv(filename)

    output['sites_per_km2'] = output.sites_per_km2.round(4)

    output['inter_site_distance_km'] = output['inter_site_distance_m'] / 1e3

    output = output[['inter_site_distance_km', 'site_area_km2', 'sites_per_km2',
        'capacity_mbps_km2', 'capacity_mbps',
        'environment',
        'ran_sector_antenna_costs_km2',
        'ran_remote_radio_unit_costs_km2', 'ran_baseband_unit_costs_km2',
        'ran_router_costs_km2', 'civil_tower_costs_km2',
        'civil_material_costs_km2', 'civil_transportation_costs_km2',
        'civil_installation_costs_km2', 'power_battery_system_costs_km2',
        'backhaul_fiber_backhaul_costs_km2',
        'backhaul_microwave_backhaul_1m_costs_km2'
    ]]

    output = output.reset_index().reset_index(drop=True)

    ISD = output.inter_site_distance_km.astype(int) < max_isd_distance
    output = output[ISD]

    return output

def generate_long_data(data, x_axis_metric_lower, x_axis_metric_final):

    output = data[[
        x_axis_metric_lower,
        'capacity_mbps_km2',
        'environment',
        'ran_sector_antenna_costs_km2',
        'ran_remote_radio_unit_costs_km2', 'ran_baseband_unit_costs_km2',
        'ran_router_costs_km2', 'civil_tower_costs_km2',
        'civil_material_costs_km2', 'civil_transportation_costs_km2',
        'civil_installation_costs_km2', 'power_battery_system_costs_km2',
        'backhaul_fiber_backhaul_costs_km2',
        'backhaul_microwave_backhaul_1m_costs_km2'
    ]]

    output = pd.melt(output,
        id_vars=[x_axis_metric_lower, 'environment'],
        value_vars=[
            'ran_sector_antenna_costs_km2',
            'ran_remote_radio_unit_costs_km2',
            'ran_baseband_unit_costs_km2',
            'ran_router_costs_km2', 'civil_tower_costs_km2',
            'civil_material_costs_km2', 'civil_transportation_costs_km2',
            'civil_installation_costs_km2', 'power_battery_system_costs_km2',
            'backhaul_fiber_backhaul_costs_km2',
            'backhaul_microwave_backhaul_1m_costs_km2'
        ])

    output.columns = ['x_axis_value', 'Environment', 'Component', 'gross_value']

    output['Value'] = round(output['gross_value'] / 1000)

    output = output[['x_axis_value', 'Environment', 'Component', 'Value']]

    output['Metric'] = output['Component'].str.split("_", n = 1, expand = True) [0]

    output = output.replace(
        {
            'Metric':{
                'ran': 'RAN',
                'civil': 'Civil works',
                'power': 'Power',
                'backhaul': 'Backhaul',
            }
        }
    )

    output = output.replace(
        {
            'Environment':{
                'urban': 'Urban',
                'suburban': 'Suburban',
                'rural': 'Rural',
            }
        }
    )

    return output


def plotting_function3(data):

    data_isd = generate_long_data(data, 'inter_site_distance_km', 'ISD')
    data_isd['Density Metric'] = 'ISD (km)'

    #'site_area_km2', 'sites_per_km2',
    data_density = generate_long_data(data, 'sites_per_km2', 'Site Density (km^2)')
    data_density['Density Metric'] = 'Site Density (km^2)'

    all_data = pd.concat([data_isd, data_density], axis= 0)

    all_data['x_axis_value'] = round(all_data['x_axis_value'], 3)

    bins = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    all_data['x_axis_value_binned'] = pd.cut(all_data['x_axis_value'], bins)

    plot = sns.catplot(x='x_axis_value_binned', y='Value', hue="Metric", kind='bar',
        row="Environment", col='Density Metric',# col_wrap=1,
        data=all_data, palette=sns.color_palette("husl", 5),
        sharey=True, sharex=False, legend="full")

    plot.set_xticklabels(rotation=45)

    plot.axes[0,0].set_ylabel('Cost (USD$k)')
    plot.axes[1,0].set_ylabel('Cost (USD$k)')
    plot.axes[2,0].set_ylabel('Cost (USD$k)')

    plot.axes[0,1].set_xlabel('')
    plot.axes[1,1].set_xlabel('')
    plot.axes[2,1].set_xlabel('')
    plot.axes[2,0].set_xlabel('')

    plt.subplots_adjust(hspace=0.4, wspace=0.05, bottom=0.3)

    plot.savefig(DATA_OUTPUT + '/costs_capacity_barplot_isd_density.png')

    return print('completed (capacity-cost) replot (isd)')


if __name__ == '__main__':

    # data = load_in_all_main_lut()

    # plotting_function1(data)

    # plotting_function1_isd(data)

    # plotting_function2(data)

    max_isd_distance = 10

    data = load_summary_lut(max_isd_distance)

    plotting_function3(data)
