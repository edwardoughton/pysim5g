"""
Runner for system_simulator.py

Written by Edward Oughton
May 2019

"""
import os
import sys
import configparser
import csv

import math
import fiona
from shapely.geometry import shape, Point, LineString, mapping
import numpy as np
from random import choice
from rtree import index

from collections import OrderedDict

from pysim5g.generate_hex import produce_sites_and_site_areas
from pysim5g.system_simulator import SimulationManager
from pysim5g.costs import calculate_costs

np.random.seed(42)

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']


def generate_receivers(site_area, parameters, grid):
    """

    Generate receiver locations as points within the site area.

    Sampling points can either be generated on a grid (grid=1)
    or more efficiently between the transmitter and the edge
    of the site (grid=0) area.

    Parameters
    ----------
    site_area : polygon
        Shape of the site area we want to generate receivers within.
    parameters : dict
        Contains all necessary simulation parameters.
    grid : int
        Binary indicator to dictate receiver generation type.

    Output
    ------
    receivers : List of dicts
        Contains the quantity of desired receivers within the area boundary.

    """
    receivers = []

    if grid == 1:

        geom = shape(site_area[0]['geometry'])
        geom_box = geom.bounds

        minx = geom_box[0]
        miny = geom_box[1]
        maxx = geom_box[2]
        maxy = geom_box[3]

        id_number = 0

        x_axis = np.linspace(
            minx, maxx, num=(
                int(math.sqrt(geom.area) / (math.sqrt(geom.area)/20))
                )
            )
        y_axis = np.linspace(
            miny, maxy, num=(
                int(math.sqrt(geom.area) / (math.sqrt(geom.area)/20))
                )
            )

        xv, yv = np.meshgrid(x_axis, y_axis, sparse=False, indexing='ij')
        for i in range(len(x_axis)):
            for j in range(len(y_axis)):
                receiver = Point((xv[i,j], yv[i,j]))
                indoor_outdoor_probability = np.random.rand(1,1)[0][0]
                if geom.contains(receiver):
                    receivers.append({
                        'type': "Feature",
                        'geometry': {
                            "type": "Point",
                            "coordinates": [xv[i,j], yv[i,j]],
                        },
                        'properties': {
                            'ue_id': "id_{}".format(id_number),
                            "misc_losses": parameters['rx_misc_losses'],
                            "gain": parameters['rx_gain'],
                            "losses": parameters['rx_losses'],
                            "ue_height": float(parameters['rx_height']),
                            "indoor": (True if float(indoor_outdoor_probability) < \
                                float(0.5) else False),
                        }
                    })
                    id_number += 1

                else:
                    pass

    else:

        centroid = shape(site_area[0]['geometry']).centroid

        coord = site_area[0]['geometry']['coordinates'][0][0]
        path = LineString([(coord), (centroid)])
        length = int(path.length)
        increment = int(length / 20)

        indoor = parameters['indoor_users_percentage'] / 100

        id_number = 0
        for increment_value in range(1, 11):
            point = path.interpolate(increment * increment_value)
            indoor_outdoor_probability = np.random.rand(1,1)[0][0]
            receivers.append({
                'type': "Feature",
                'geometry': mapping(point),
                'properties': {
                    'ue_id': "id_{}".format(id_number),
                    "misc_losses": parameters['rx_misc_losses'],
                    "gain": parameters['rx_gain'],
                    "losses": parameters['rx_losses'],
                    "ue_height": float(parameters['rx_height']),
                    "indoor": (True if float(indoor_outdoor_probability) < \
                        float(indoor) else False),
                }
            })
            id_number += 1

    return receivers


def obtain_percentile_values(results, transmission_type, parameters):
    """

    Get the threshold value for a metric based on a given percentile.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.

    parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    percentile_site_results : dict
        Contains the percentile value for each site metric.

    """
    percentile = parameters['percentile']

    path_loss_values = []
    received_power_values = []
    interference_values = []
    sinr_values = []
    spectral_efficiency_values = []
    estimated_capacity_values = []
    estimated_capacity_values_km2 = []

    for result in results:

        path_loss_values.append(result['path_loss'])

        received_power_values.append(result['received_power'])

        interference_values.append(result['interference'])

        sinr = result['sinr']
        if sinr == None:
            sinr = 0
        else:
            sinr_values.append(sinr)

        spectral_efficiency = result['spectral_efficiency']
        if spectral_efficiency == None:
            spectral_efficiency = 0
        else:
            spectral_efficiency_values.append(spectral_efficiency)

        estimated_capacity = result['capacity_mbps']
        if estimated_capacity == None:
            estimated_capacity = 0
        else:
            estimated_capacity_values.append(estimated_capacity)

        estimated_capacity_km2 = result['capacity_mbps_km2']
        if estimated_capacity_km2 == None:
            estimated_capacity_km2 = 0
        else:
            estimated_capacity_values_km2.append(estimated_capacity_km2)

    percentile_site_results = {
        'results_type': (
            '{}_percentile'.format(percentile)
        ),
        'tranmission_type': transmission_type,
        'path_loss': np.percentile(
            path_loss_values, percentile
        ),
        'received_power': np.percentile(
            received_power_values, percentile
        ),
        'interference': np.percentile(
            interference_values, percentile
        ),
        'sinr': np.percentile(
            sinr_values, percentile
        ),
        'spectral_efficiency': np.percentile(
            spectral_efficiency_values, percentile
        ),
        'capacity_mbps': np.percentile(
            estimated_capacity_values, percentile
        ),
        'capacity_mbps_km2': np.percentile(
            estimated_capacity_values_km2, percentile
        ),
    }

    return percentile_site_results


def get_lookup_table(lut, transmission_type):
    """
    Subsets the lookup table based on the transmission type.

    Parameters
    ----------
    transmission_type : string
        Either SISO (1x1), or MIMO (4x4, 8x8 etc.)

    Returns
    -------
    output : list
        Subset of lookup table.

    """
    output = []

    #('4G', '1x1', 1, 'QPSK', 78,	0.1523, -6.7),
    for item in lut:
        if item[1] == transmission_type:
            output.append(
                item
            )

    return output


def obtain_threshold_values_choice(results, parameters):
    """

    Get the threshold capacity based on a given percentile.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.
    parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    matching_result : float
        Contains the chosen percentile value based on the input data.

    """
    sinr_values = []

    percentile = parameters['percentile']

    for result in results:

        sinr = result['sinr']

        if sinr == None:
            pass
        else:
            sinr_values.append(sinr)

    sinr = np.percentile(sinr_values, percentile, interpolation='nearest')

    matching_result = []

    for result in results:
        if float(result['sinr']) == float(sinr):
            matching_result.append(result)

    return float(choice(matching_result))


def convert_results_geojson(data):
    """

    Convert results to geojson format, for writing to shapefile.

    Parameters
    ----------
    data : list of dicts
        Contains all results ready to be written.

    Outputs
    -------
    output : list of dicts
        A list of geojson dictionaries ready for writing.

    """
    output = []

    for datum in data:
        output.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    datum['receiver_x'], datum['receiver_y']]
                },
            'properties': {
                'path_loss': float(datum['path_loss']),
                'received_power': float(datum['received_power']),
                'interference': float(datum['interference']),
                'noise': float(datum['noise']),
                'sinr': float(datum['sinr']),
                'spectral_efficiency': float(
                    datum['spectral_efficiency']
                ),
                'capacity_mbps': float(
                    datum['capacity_mbps']
                ),
                'capacity_mbps_km2': float(
                    datum['capacity_mbps_km2']
                ),
                },
            }
        )

    return output


def write_full_results(data, environment, site_radius, frequency,
    bandwidth, generation, ant_type, transmittion_type, directory,
    filename, parameters):
    """

    Write full results data to .csv.

    Parameters
    ----------
    data : list of dicts
        Contains all results ready to be written.
    environment : string
        Either urban, suburban or rural clutter type.
    site_radius : int
        Radius of site area in meters.
    frequency : float
        Spectral frequency of carrier band in GHz.
    bandwidth : int
        Channel bandwidth of carrier band in MHz.
    generation : string
        Either 4G or 5G depending on technology generation.
    ant_type : string
        The type of transmitter modelled (macro, micro etc.).
    tranmission_type : string
        The type of tranmission (SISO, MIMO 4x4, MIMO 8x8 etc.).
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    parameters : dict
        Contains all necessary simulation parameters.

    """
    sectors = parameters['sectorization']
    inter_site_distance = site_radius * 2
    site_area_km2 = (
        math.sqrt(3) / 2 * inter_site_distance ** 2 / 1e6
    )
    sites_per_km2 = 1 / site_area_km2

    if not os.path.exists(directory):
        os.makedirs(directory)

    full_path = os.path.join(directory, filename)

    results_file = open(full_path, 'w', newline='')
    results_writer = csv.writer(results_file)
    results_writer.writerow(
        (
            'environment',
            'inter_site_distance_m',
            'sites_per_km2',
            'frequency_GHz',
            'bandwidth_MHz',
            'number_of_sectors',
            'generation',
            'ant_type',
            'transmittion_type',
            'receiver_x',
            'receiver_y',
            'r_distance',
            'path_loss_dB',
            'r_model',
            'received_power_dB',
            'interference_dB',
            'i_model',
            'noise_dB',
            'sinr_dB',
            'spectral_efficiency_bps_hz',
            'capacity_mbps',
            'capacity_mbps_km2'
        )
    )

    for row in data:
        results_writer.writerow((
            environment,
            inter_site_distance,
            sites_per_km2,
            frequency,
            bandwidth,
            sectors,
            generation,
            ant_type,
            transmittion_type,
            row['receiver_x'],
            row['receiver_y'],
            row['distance'],
            row['path_loss'],
            row['r_model'],
            row['received_power'],
            row['interference'],
            row['i_model'],
            row['noise'],
            row['sinr'],
            row['spectral_efficiency'],
            row['capacity_mbps'],
            row['capacity_mbps_km2'],
            ))


def write_frequency_lookup_table(result, environment, site_radius,
    frequency, bandwidth, generation, ant_type, tranmission_type,
    directory, filename, parameters):
    """

    Write the main, comprehensive lookup table for all environments,
    site radii, frequencies etc.

    Parameters
    ----------
    results : list of dicts
        Contains all results ready to be written.
    environment : string
        Either urban, suburban or rural clutter type.
    site_radius : int
        Radius of site area in meters.
    frequency : float
        Spectral frequency of carrier band in GHz.
    bandwidth : int
        Channel bandwidth of carrier band in MHz.
    generation : string
        Either 4G or 5G depending on technology generation.
    ant_type : string
        Type of transmitters modelled.
    tranmission_type : string
        The transmission type (SISO, MIMO etc.).
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    parameters : dict
        Contains all necessary simulation parameters.

    """
    inter_site_distance = site_radius * 2
    site_area_km2 = math.sqrt(3) / 2 * inter_site_distance ** 2 / 1e6
    sites_per_km2 = 1 / site_area_km2

    sectors = parameters['sectorization']

    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = os.path.join(directory, filename)

    if not os.path.exists(directory):
        lut_file = open(directory, 'w', newline='')
        lut_writer = csv.writer(lut_file)
        lut_writer.writerow(
            (
                'results_type',
                'environment',
                'inter_site_distance_m',
                'site_area_km2',
                'sites_per_km2',
                'frequency_GHz',
                'bandwidth_MHz',
                'number_of_sectors',
                'generation',
                'ant_type',
                'transmission_type',
                'path_loss_dB',
                'received_power_dBm',
                'interference_dBm',
                'sinr_dB',
                'spectral_efficiency_bps_hz',
                'capacity_mbps',
                'capacity_mbps_km2',
            )
        )
    else:
        lut_file = open(directory, 'a', newline='')
        lut_writer = csv.writer(lut_file)

    lut_writer.writerow(
        (
            result['results_type'],
            environment,
            inter_site_distance,
            site_area_km2,
            sites_per_km2,
            frequency,
            bandwidth,
            sectors,
            generation,
            ant_type,
            tranmission_type,
            result['path_loss'],
            result['received_power'],
            result['interference'],
            result['sinr'],
            result['spectral_efficiency'],
            result['capacity_mbps'],
            result['capacity_mbps_km2'] * sectors,
        )
    )

    lut_file.close()


def write_cost_lookup_table(results, directory, filename):
    """

    Write the main, comprehensive lookup table for all environments,
    site radii, frequencies etc.

    Parameters
    ----------
    results : list of dicts
        Contains all results ready to be written.
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.

    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = os.path.join(directory, filename)

    if not os.path.exists(directory):
        lut_file = open(directory, 'w', newline='')
        lut_writer = csv.writer(lut_file)
        lut_writer.writerow(
            (
                'results_type',
                'strategy',
                'environment',
                'inter_site_distance_m',
                'site_area_km2',
                'sites_per_km2',
                'total_deployment_costs_km2',
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
                'backhaul_router_costs_km2',
            )
        )
    else:
        lut_file = open(directory, 'a', newline='')
        lut_writer = csv.writer(lut_file)

    for result in results:
        lut_writer.writerow(
            (
                result['results_type'],
                result['strategy'],
                result['environment'],
                result['inter_site_distance'],
                result['site_area_km2'],
                result['sites_per_km2'],
                result['total_deployment_costs_km2'],
                result['sector_antenna_costs_km2'],
                result['remote_radio_unit_costs_km2'],
                result['baseband_unit_costs_km2'],
                result['site_rental_km2'],
                result['tower_costs_km2'],
                result['civil_material_costs_km2'],
                result['transportation_costs_km2'],
                result['installation_costs_km2'],
                result['power_system_costs_km2'],
                result['fiber_backhaul_costs_km2'],
                result['router_costs_km2'],
            )
        )

    lut_file.close()


def write_export_strategy_costs(data_path, directory, filename):

    data = []
    isd = []

    with open(data_path, 'r') as source:
        reader = csv.DictReader(source)
        for result in reader:
            result = dict(result)
            data.append({
                'strategy': result['strategy'],
                'inter_site_distance': int(result['inter_site_distance_m']),
                'sector_antenna_costs_km2': float(result['ran_sector_antenna_costs_km2']),
                'remote_radio_unit_costs_km2': float(result['ran_remote_radio_unit_costs_km2']),
                'baseband_unit_costs_km2': float(result['ran_baseband_unit_costs_km2']),
                'site_rental_km2': float(result['site_rental_km2']),
                'tower_costs_km2': float(result['civil_tower_costs_km2']),
                'civil_material_costs_km2': float(result['civil_material_costs_km2']),
                'transportation_costs_km2': float(result['civil_transportation_costs_km2']),
                'installation_costs_km2': float(result['civil_installation_costs_km2']),
                'power_system_costs_km2': float(result['power_system_costs_km2']),
                'fiber_backhaul_costs_km2': float(result['backhaul_fiber_backhaul_costs_km2']),
                'router_costs_km2': float(result['backhaul_router_costs_km2']),
                })
            isd.append(int(result['inter_site_distance_m']))

    bins = [
        (0.5, 1.5),
        (1.5, 2.5),
        (2.5, 3.5),
        (3.5, 4.5),
        (4.5, 5.5),
    ]

    strategies = [
        'baseline',# 'Baseline (No Sharing)',
        'passive_site_sharing',# 'Passive Site Sharing',
        'passive_backhaul_sharing',# 'Passive Backhaul Sharing',
        'active_moran',# 'Multi Operator RAN',
    ]

    intermediate = []

    #get the average values across strategies and each bin range
    for strategy in strategies:
        for lower, upper in bins:

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

            for item in data:
                if item['strategy'] == strategy:
                    if lower <= (int(item['inter_site_distance'])/1e3) < upper:
                        ran_sector_antenna_costs_km2.append(item['sector_antenna_costs_km2'])
                        ran_remote_radio_unit_costs_km2.append(item['remote_radio_unit_costs_km2'])
                        ran_baseband_unit_costs_km2.append(item['baseband_unit_costs_km2'])
                        site_rental_km2.append(item['site_rental_km2'])
                        civil_tower_costs_km2.append(item['tower_costs_km2'])
                        civil_material_costs_km2.append(item['civil_material_costs_km2'])
                        civil_transportation_costs_km2.append(item['transportation_costs_km2'])
                        civil_installation_costs_km2.append(item['installation_costs_km2'])
                        power_system_costs_km2.append(item['power_system_costs_km2'])
                        backhaul_fiber_backhaul_costs_km2.append(item['fiber_backhaul_costs_km2'])
                        backhaul_router_costs_km2.append(item['router_costs_km2'])

            if len(ran_sector_antenna_costs_km2) == 0:
                continue

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
            })

    unique_isd = set()
    unique_strategies = set()
    cost_saving_by_strategy = []
    results = []

    #write results out by individual equipment type
    for item in intermediate:

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
                if key.startswith('RAN'):
                    ran_cost += value
                if key.startswith('Site'):
                    site_rental += value
                if key.startswith('Civil'):
                    civils_cost += value
                if key.startswith('Power'):
                    power_cost += value
                if key.startswith('Backhaul'):
                    backhaul_cost += value
                total_cost += value

        results.append({
            'Results Type': item['Results Type'],
            'Strategy': item['Strategy'],
            'ISD (km)': item['ISD (km)'],
            'RAN': round(ran_cost),
            'Site Rental': round(site_rental),
            'Civil': round(civils_cost),
            'Power': round(power_cost),
            'Backhaul': round(backhaul_cost),
            'Total': round(total_cost),
        })

        results.append({
            'Results Type': 'Percentage (%)',
            'Strategy': item['Strategy'],
            'ISD (km)': item['ISD (km)'],
            'RAN': round(ran_cost / total_cost * 100, 2),
            'Site Rental': round(site_rental / total_cost * 100, 2),
            'Civil': round(civils_cost / total_cost * 100, 2),
            'Power': round(power_cost / total_cost * 100, 2),
            'Backhaul': round(backhaul_cost / total_cost * 100, 2),
            'Total': 100
        })

        if item['Results Type'] == 'Raw ($/km2)':
            cost_saving_by_strategy.append({
                'Strategy': item['Strategy'],
                'ISD (km)': item['ISD (km)'],
                'Total': total_cost,
            })

    results_to_write = []
    for strategy in list(unique_strategies):
        for isd in list(unique_isd):
            for item in cost_saving_by_strategy:
                if item['Strategy'] == 'baseline' and item['ISD (km)'] == isd:
                    baseline_total_cost = item['Total']
            for item in cost_saving_by_strategy:
                if item['Strategy'] == strategy and item['ISD (km)'] == isd:
                    total_cost = item['Total']
            if strategy == 'baseline':
                saving = 0
            else:
                saving = 100 - round(total_cost / baseline_total_cost * 100, 2)

            for item in results:
                if item['Strategy'] == strategy and item['ISD (km)'] == isd:
                    item['Saving on Baseline (%)'] = saving
                    results_to_write.append(item)

            baseline_total_cost = 0

    if not os.path.exists(directory):
        os.makedirs(directory)

    directory = os.path.join(directory, filename)

    if not os.path.exists(directory):
        lut_file = open(directory, 'w', newline='')
        lut_writer = csv.writer(lut_file)
        lut_writer.writerow(
            (
                'Results Type',
                'Strategy',
                'ISD (km)',
                'RAN',
                'Site Rental',
                'Civils',
                'Power',
                'Backhaul',
                'Total',
                'Saving (%)',
            )
        )
    else:
        lut_file = open(directory, 'a', newline='')
        lut_writer = csv.writer(lut_file)

    for result in results_to_write:

        if result['Strategy'] == 'baseline':
            strategy = 'Baseline (No Sharing)'
        elif result['Strategy'] == 'passive_site_sharing':
            strategy = 'Passive Site Sharing'
        elif result['Strategy'] == 'passive_backhaul_sharing':
            strategy = 'Passive Backhaul Sharing'
        elif result['Strategy'] == 'active_moran':
            strategy = 'Multi-Operator RAN'

        lut_writer.writerow(
            (
                result['Results Type'],
                strategy,
                result['ISD (km)'],
                round(result['RAN'], 2),
                round(result['Site Rental'], 2),
                round(result['Civil'], 2),
                round(result['Power'], 2),
                round(result['Backhaul'], 2),
                round(result['Total'], 2),
                round(result['Saving (%)'], 2),
            )
        )

    lut_file.close()


def write_shapefile(data, directory, filename, crs):
    """

    Write geojson data to shapefile.

    """
    prop_schema = []
    for name, value in data[0]['properties'].items():
        fiona_prop_type = next((
            fiona_type for fiona_type, python_type in \
                fiona.FIELD_TYPES_MAP.items() if \
                python_type == type(value)), None
            )

        prop_schema.append((name, fiona_prop_type))

    sink_driver = 'ESRI Shapefile'
    sink_crs = {'init': crs}
    sink_schema = {
        'geometry': data[0]['geometry']['type'],
        'properties': OrderedDict(prop_schema)
    }

    if not os.path.exists(directory):
        os.makedirs(directory)

    with fiona.open(
        os.path.join(directory, filename), 'w',
        driver=sink_driver, crs=sink_crs, schema=sink_schema) as sink:
        for datum in data:
            sink.write(datum)


def run_simulator(parameters, spectrum_portfolio, ant_types,
    tranmission_types, site_radii, modulation_and_coding_lut, costs):
    """

    Function to run the simulator and all associated modules.

    """
    unprojected_point = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': (-0.07496, 51.42411),
            },
        'properties': {
            'site_id': 'Crystal Palace Radio Tower'
            }
        }

    unprojected_crs = 'epsg:4326'
    projected_crs = 'epsg:3857'

    environments =[
        'urban',
        'suburban',
        'rural'
    ]

    for environment in environments:
        for ant_type in ant_types:
            site_radii_generator = site_radii[ant_type]
            for site_radius in site_radii_generator[environment]:
                for transmission_type in tranmission_types:

                    lut = get_lookup_table(modulation_and_coding_lut, transmission_type)

                    print('--working on {}: {} ({})'.format(environment, site_radius,
                        transmission_type))

                    transmitter, interfering_transmitters, site_area, int_site_areas = \
                        produce_sites_and_site_areas(
                            unprojected_point['geometry']['coordinates'],
                            site_radius,
                            unprojected_crs,
                            projected_crs
                            )

                    receivers = generate_receivers(site_area, PARAMETERS, 1)

                    for frequency, bandwidth, generation in spectrum_portfolio:

                        if generation == '4G' and not transmission_type == '1x1':
                            continue

                        MANAGER = SimulationManager(
                            transmitter, interfering_transmitters, ant_type,
                            receivers, site_area, PARAMETERS
                            )

                        results = MANAGER.estimate_link_budget(
                            frequency,
                            bandwidth,
                            generation,
                            ant_type,
                            transmission_type,
                            environment,
                            lut,
                            parameters
                            )

                        folder = os.path.join(BASE_PATH, '..', 'results', 'full_tables')
                        filename = 'full_capacity_lut_{}_{}_{}_{}_{}.csv'.format(
                            environment, site_radius, frequency, ant_type, transmission_type)

                        write_full_results(results, environment, site_radius,
                            frequency, bandwidth, generation, ant_type, transmission_type,
                            folder, filename, parameters)

                        percentile_site_results = obtain_percentile_values(
                            results, transmission_type, parameters
                        )

                        results_directory = os.path.join(BASE_PATH, '..', 'results')
                        write_frequency_lookup_table(percentile_site_results, environment,
                            site_radius, frequency, bandwidth, generation,
                            ant_type, transmission_type, results_directory,
                            'capacity_lut_by_frequency_{}.csv'.format(parameters['percentile']),
                            parameters
                        )

                        # if frequency == spectrum_portfolio[0][0]:

                        #     percentile_site_results = calculate_costs(
                        #         percentile_site_results, costs, parameters,
                        #         site_radius, environment
                        #     )

                        #     write_cost_lookup_table(percentile_site_results, results_directory,
                        #         'percentile_{}_capacity_lut.csv'.format(
                        #         parameters['percentile'])
                        #     )

    #                     # geojson_receivers = convert_results_geojson(results)

    #                     # write_shapefile(
    #                     #     geojson_receivers, os.path.join(results_directory, 'shapes'),
    #                     #     'receivers_{}.shp'.format(site_radius),
    #                     #     projected_crs
    #                     #     )

    #                     # write_shapefile(
    #                     #     transmitter, os.path.join(results_directory, 'shapes'),
    #                     #     'transmitter_{}.shp'.format(site_radius),
    #                     #     projected_crs
    #                     # )

    #                     # write_shapefile(
    #                     #     site_area, os.path.join(results_directory, 'shapes'),
    #                     #     'site_area_{}.shp'.format(site_radius),
    #                     #     projected_crs
    #                     # )

    #                     # write_shapefile(
    #                     #     interfering_transmitters, os.path.join(results_directory, 'shapes'),
    #                     #     'interfering_transmitters_{}.shp'.format(site_radius),
    #                     #     projected_crs
    #                     # )

    #                     # write_shapefile(
    #                     #     interfering_site_areas, os.path.join(results_directory, 'shapes'),
    #                     #     'interfering_site_areas_{}.shp'.format(site_radius),
    #                     #     projected_crs
    #                     # )

    # # write_export_strategy_costs(os.path.join(results_directory,
    # #     'percentile_{}_capacity_lut.csv'.format(PARAMETERS['percentile'])),
    # #     results_directory,
    # #     'aggregate_strategy_costs.csv'.format(PARAMETERS['percentile'])
    # # )

if __name__ == '__main__':

    PARAMETERS = {
        'iterations': 1,
        'seed_value1': 1,
        'seed_value2': 2,
        'indoor_users_percentage': 50,
        'los_breakpoint_m': 500,
        'tx_macro_baseline_height': 30,
        'tx_macro_power': 40,
        'tx_macro_gain': 16,
        'tx_macro_losses': 1,
        'tx_micro_baseline_height': 10,
        'tx_micro_power': 24,
        'tx_micro_gain': 5,
        'tx_micro_losses': 1,
        'rx_gain': 4,
        'rx_losses': 4,
        'rx_misc_losses': 4,
        'rx_height': 1.5,
        'building_height': 5,
        'street_width': 20,
        'above_roof': 0,
        'network_load': 50,
        'percentile': 50,
        'sectorization': 3,
        'mnos': 2,
        'asset_lifetime': 10,
        'discount_rate': 3.5,
        'opex_percentage_of_capex': 10,
    }

    COSTS = {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'single_baseband_unit': 10000,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 10000,
        'installation': 5000,
        'site_rental': 9600,
        'power_generator_battery_system': 5000,
        'high_speed_backhaul_hub': 15000,
        'router': 2000,
    }

    SPECTRUM_PORTFOLIO = [
        (0.7, 10, '5G'),
        (0.8, 10, '4G'),
        (1.8, 10, '4G'),
        (2.6, 10, '4G'),
        (3.5, 50, '5G'),
        (3.7, 50, '5G'),
        (26, 500, '5G'),
    ]

    ANT_TYPE = [
        ('macro'),
        ('micro'),
    ]

    TRANSMISSION_TYPES = [
        '1x1',
        # '4x4',
        '8x8',
    ]

    MODULATION_AND_CODING_LUT =[
        # ETSI. 2018. ‘5G; NR; Physical Layer Procedures for Data
        # (3GPP TS 38.214 Version 15.3.0 Release 15)’. Valbonne, France: ETSI.
        # Generation MIMO CQI Index	Modulation	Coding rate
        # Spectral efficiency (bps/Hz) SINR estimate (dB)
        ('4G', '1x1', 1, 'QPSK', 78, 0.1523, -6.7),
        ('4G', '1x1', 2, 'QPSK', 120, 0.2344, -4.7),
        ('4G', '1x1', 3, 'QPSK', 193, 0.377, -2.3),
        ('4G', '1x1', 4, 'QPSK', 308, 0.6016, 0.2),
        ('4G', '1x1', 5, 'QPSK', 449, 0.877, 2.4),
        ('4G', '1x1', 6, 'QPSK', 602, 1.1758, 4.3),
        ('4G', '1x1', 7, '16QAM', 378, 1.4766, 5.9),
        ('4G', '1x1', 8, '16QAM', 490, 1.9141, 8.1),
        ('4G', '1x1', 9, '16QAM', 616, 2.4063, 10.3),
        ('4G', '1x1', 10, '64QAM', 466, 2.7305, 11.7),
        ('4G', '1x1', 11, '64QAM', 567, 3.3223, 14.1),
        ('4G', '1x1', 12, '64QAM', 666, 3.9023, 16.3),
        ('4G', '1x1', 13, '64QAM', 772, 4.5234, 18.7),
        ('4G', '1x1', 14, '64QAM', 973, 5.1152, 21),
        ('4G', '1x1', 15, '64QAM', 948, 5.5547, 22.7),
        ('5G', '1x1', 1, 'QPSK', 78, 0.1523, -6.7),
        ('5G', '1x1', 2, 'QPSK', 193, 0.377, -4.7),
        ('5G', '1x1', 3, 'QPSK', 449, 0.877, -2.3),
        ('5G', '1x1', 4, '16QAM', 378, 1.4766, 0.2),
        ('5G', '1x1', 5, '16QAM', 490, 1.9141, 2.4),
        ('5G', '1x1', 6, '16QAM', 616, 2.4063, 4.3),
        ('5G', '1x1', 7, '64QAM', 466, 2.7305, 5.9),
        ('5G', '1x1', 8, '64QAM', 567, 3.3223, 8.1),
        ('5G', '1x1', 9, '64QAM', 666, 3.9023, 10.3),
        ('5G', '1x1', 10, '64QAM', 772, 4.5234, 11.7),
        ('5G', '1x1', 11, '64QAM', 873, 5.1152, 14.1),
        ('5G', '1x1', 12, '256QAM', 711, 5.5547, 16.3),
        ('5G', '1x1', 13, '256QAM', 797, 6.2266, 18.7),
        ('5G', '1x1', 14, '256QAM', 885, 6.9141, 21),
        ('5G', '1x1', 15, '256QAM', 948, 7.4063, 22.7),
        ('5G', '4x4', 1, 'QPSK', 78, 0.15, -6.7),
        ('5G', '4x4', 2, 'QPSK', 193, 1.02, -4.7),
        ('5G', '4x4', 3, 'QPSK', 449, 2.21, -2.3),
        ('5G', '4x4', 4, '16QAM', 378, 3.20, 0.2),
        ('5G', '4x4', 5, '16QAM', 490, 4.00, 2.4),
        ('5G', '4x4', 6, '16QAM', 616, 5.41, 4.3),
        ('5G', '4x4', 7, '64QAM', 466, 6.20, 5.9),
        ('5G', '4x4', 8, '64QAM', 567, 8.00, 8.1),
        ('5G', '4x4', 9, '64QAM', 666, 9.50, 10.3),
        ('5G', '4x4', 10, '64QAM', 772, 11.00, 11.7),
        ('5G', '4x4', 11, '64QAM', 873, 14.00, 14.1),
        ('5G', '4x4', 12, '256QAM', 711, 16.00, 16.3),
        ('5G', '4x4', 13, '256QAM', 797, 19.00, 18.7),
        ('5G', '4x4', 14, '256QAM', 885, 22.00, 21),
        ('5G', '4x4', 15, '256QAM', 948, 25.00, 22.7),
        ('5G', '8x8', 1, 'QPSK', 78, 0.30, -6.7),
        ('5G', '8x8', 2, 'QPSK', 193, 2.05, -4.7),
        ('5G', '8x8', 3, 'QPSK', 449, 4.42, -2.3),
        ('5G', '8x8', 4, '16QAM', 378, 6.40, 0.2),
        ('5G', '8x8', 5, '16QAM', 490, 8.00, 2.4),
        ('5G', '8x8', 6, '16QAM', 616, 10.82, 4.3),
        ('5G', '8x8', 7, '64QAM', 466, 12.40, 5.9),
        ('5G', '8x8', 8, '64QAM', 567, 16.00, 8.1),
        ('5G', '8x8', 9, '64QAM', 666, 19.00, 10.3),
        ('5G', '8x8', 10, '64QAM', 772, 22.00, 11.7),
        ('5G', '8x8', 11, '64QAM', 873, 28.00, 14.1),
        ('5G', '8x8', 12, '256QAM', 711, 32.00, 16.3),
        ('5G', '8x8', 13, '256QAM', 797, 38.00, 18.7),
        ('5G', '8x8', 14, '256QAM', 885, 44.00, 21),
        ('5G', '8x8', 15, '256QAM', 948, 50.00, 22.7),
    ]

    def generate_site_radii(min, max, increment):
        for n in range(min, max, increment):
            yield n

    INCREMENT_MA = (400, 30400, 1000) #(5000, 5500, 500) #
    INCREMENT_MI = (40, 540, 100)

    SITE_RADII = {
        'macro': {
            'urban':
                generate_site_radii(INCREMENT_MA[0],INCREMENT_MA[1],INCREMENT_MA[2]),
            'suburban':
                generate_site_radii(INCREMENT_MA[0],INCREMENT_MA[1],INCREMENT_MA[2]),
            'rural':
                generate_site_radii(INCREMENT_MA[0],INCREMENT_MA[1],INCREMENT_MA[2])
            },
        'micro': {
            'urban':
                generate_site_radii(INCREMENT_MI[0],INCREMENT_MI[1],INCREMENT_MI[2]),
            'suburban':
                generate_site_radii(INCREMENT_MI[0],INCREMENT_MI[1],INCREMENT_MI[2]),
            'rural':
                generate_site_radii(INCREMENT_MI[0],INCREMENT_MI[1],INCREMENT_MI[2])
            },
        }

    run_simulator(
        PARAMETERS,
        SPECTRUM_PORTFOLIO,
        ANT_TYPE,
        TRANSMISSION_TYPES,
        SITE_RADII,
        MODULATION_AND_CODING_LUT,
        COSTS
        )
