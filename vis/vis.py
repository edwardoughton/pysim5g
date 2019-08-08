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
CONFIG.read(os.path.join(os.path.dirname(__file__),'..','..','scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA = os.path.join(BASE_PATH, 'intermediate', 'system_simulator')
DATA_OUTPUT = os.path.join(BASE_PATH, '..', 'vis', 'vis_5g', 'figures')

if not os.path.exists(DATA_OUTPUT):
    os.mkdir(DATA_OUTPUT)

def load_in_all_main_lut():

    filenames = glob.iglob(os.path.join(DATA, '**/*test_lookup_table*'), recursive=True)

    output = pd.concat((pd.read_csv(f) for f in filenames))

    output['capacity_per_Hz_km2'] = (
        output['three_sector_capacity_mbps_km2'] / (output['bandwidth_MHz'] * 1e6)
        )

    output['sites_per_km2'] = output.sites_per_km2.round(1)

    output['inter_site_distance_km'] = output['inter_site_distance'] / 1e3

    return output


def plot_main_lut(data):

    data['environment'] = data['environment'].replace(
        {
            'urban': 'Urban',
            'suburban': 'Suburban',
            'rural': 'Rural'
        }
    )

    area_types = [
        # 'urban',
        # 'suburban',
        # 'rural',
        'all'
    ]

    for area_type in area_types:

        if not area_type == 'all':
            plotting_data = data.loc[data['environment'] == area_type]

        else:
            plotting_data = data

        plotting_function1(plotting_data, area_type)

        plotting_function3(plotting_data, 'path_loss_dB', 'Path Loss (dB)')
        plotting_function3(plotting_data, 'received_power_dBm', 'Received Power (dBm)')
        plotting_function3(plotting_data, 'interference_dBm', 'Interference (dBm)')
        plotting_function3(plotting_data, 'sinr', 'SINR')
        plotting_function3(plotting_data, 'spectral_efficiency_bps_hz', 'Spectral Efficiency (Bps/Hz)')
        plotting_function3(plotting_data, 'three_sector_capacity_mbps_km2', 'Average Capacity (Mbps/km^2)')

    return ('complete')


def plotting_function1(data, filename):

    data_subset = data[['sites_per_km2','frequency_GHz','mast_height_m',
    'sinr', 'spectral_efficiency_bps_hz', 'capacity_per_Hz_km2']]

    data_subset.columns = ['Density (Km^2)', 'Frequency (GHz)', 'Height (m)',
        'SINR', 'SE', 'Capacity']

    long_data = pd.melt(data_subset,
        id_vars=['Density (Km^2)', 'Frequency (GHz)', 'Height (m)'],
        value_vars=['SINR', 'SE', 'Capacity'])

    long_data.columns = ['Density (Km^2)', 'Frequency (GHz)', 'Height (m)',
        'Metric', 'Value']

    sns.set(font_scale=1.1)

    plot = sns.catplot(x='Density (Km^2)', y='Value', hue="Frequency (GHz)",
        kind="bar", col="Height (m)", row="Metric", data=long_data,
        sharey='row')

    plot.axes[0,0].set_ylabel('SINR (dB)')
    plot.axes[1,0].set_ylabel('SE (Bps/Hz)')
    plot.axes[2,0].set_ylabel('Capacity (Bps/Hz/Km^2)')

    plot.savefig(DATA_OUTPUT + '/capacity_barplot1_{}.png'.format(filename))

    return 'completed {}'.format(filename)


def plotting_function3(data, metric_lower, metric_higher):

    data_subset = data[['inter_site_distance_km','frequency_GHz','mast_height_m',
    metric_lower, 'spectral_efficiency_bps_hz', 'capacity_per_Hz_km2', 'environment']]

    data_subset.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)',
        metric_higher, 'SE', 'Capacity', 'Env']

    # data_subset = data_subset[data_subset['Inter-Site Distance (km)'].isin([
    #     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])]

    plot = sns.FacetGrid(data_subset, row="Env", col="Height (m)", hue="Frequency (GHz)")

    plot.map(sns.lineplot, "Inter-Site Distance (km)", metric_higher).add_legend()

    plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.06)

    plot.savefig(DATA_OUTPUT + '/{}_facet.png'.format(metric_lower))

    return 'completed {}'.format(metric_lower)


def load_in_individual_luts():

    filenames = glob.iglob(os.path.join(DATA, '**/*test_capacity_data*.csv'), recursive=True)

    output = pd.concat((pd.read_csv(f) for f in filenames))

    output['capacity_per_Hz_km2'] = (
        output['estimated_capacity'] / (output['bandwidth'] * 1e6)
        )

    output['sites_per_km2'] = output.sites_per_km2.round(1)

    output['inter_site_distance_km'] = output['inter_site_distance'] / 1e3

    return output


def plot_individual_luts(data):

    # data = data[data['inter_site_distance_km'].isin([
    #     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])]

    # data = data[data['inter_site_distance_km'].isin([
    #     1, 2, 3, 4, 5, 6, 10, 15, 20, 25, 30, 35])]

    data = data.replace(
        {
            'environment':{
                'urban': 'Urban',
                'suburban': 'Suburban',
                'rural': 'Rural',
            }
        }
    )

    plotting_function6(data)

    plotting_function7(data)

    return ('complete')


def plotting_function6(data):

    data_subset = data[['inter_site_distance_km','frequency','mast_height',
    'path_loss', 'received_power', 'interference', 'environment']]

    data_subset.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)',
        'Path Loss', 'Received Power', 'Interference', 'Environment']

    long_data = pd.melt(data_subset,
        id_vars=['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)', 'Environment'],
        value_vars=['Path Loss', 'Received Power', 'Interference'])

    long_data.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)',
    'Environment', 'Metric', 'Value']

    ax = sns.relplot(x="Inter-Site Distance (km)", y='Value', hue="Environment", row="Metric",
        col='Height (m)', kind="line", data=long_data, palette=sns.set_palette("husl"),
        facet_kws=dict(sharex=False, sharey=False), hue_order=["Urban", "Suburban", "Rural"],
        legend="full",)

    handles = ax._legend_data.values()
    labels = ax._legend_data.keys()
    ax._legend.remove()
    ax.fig.legend(handles=handles, labels=labels, loc='lower center', ncol=4)

    ax.axes[0,0].set_ylabel('Path Loss (dB)')
    ax.axes[1,0].set_ylabel('Receiver Power (dB)')
    ax.axes[2,0].set_ylabel('Interference (dB)')

    plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.07)

    ax.savefig(DATA_OUTPUT + '/facet_lineplot_1.png')

    plt.cla()

    return print('completed')


def plotting_function7(data):

    data_subset = data[['inter_site_distance_km','frequency','mast_height',
    'sinr', 'spectral_efficiency', 'estimated_capacity', 'environment']]

    data_subset.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)',
        'SINR', 'SE', 'Capacity', 'Environment']

    long_data = pd.melt(data_subset,
        id_vars=['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)', 'Environment'],
        value_vars=['SINR', 'SE', 'Capacity'])

    long_data.columns = ['Inter-Site Distance (km)', 'Frequency (GHz)', 'Height (m)',
    'Environment', 'Metric', 'Value']

    ax = sns.relplot(x="Inter-Site Distance (km)", y='Value', hue="Environment", row="Metric",
        col='Height (m)', kind="line", data=long_data, palette=sns.set_palette("husl"),
        facet_kws=dict(sharex=False, sharey=False), hue_order=["Urban", "Suburban", "Rural"],
        legend="full")

    ax.axes[0,0].set_ylabel('SINR')
    ax.axes[1,0].set_ylabel('SE (Bps/Hz)')
    ax.axes[2,0].set_ylabel('Capacity (Mbps/km^2)')

    handles = ax._legend_data.values()
    labels = ax._legend_data.keys()
    ax._legend.remove()
    ax.fig.legend(handles=handles, labels=labels, loc='lower center', ncol=4)

    plt.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.07)

    ax.savefig(DATA_OUTPUT + '/facet_lineplot2.png')

    plt.cla()

    return print('completed')


if __name__ == '__main__':

    data = load_in_all_main_lut()

    plot_main_lut(data)

    individual_data = load_in_individual_luts()

    plot_individual_luts(individual_data)
