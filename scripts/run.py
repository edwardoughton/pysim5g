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


def generate_receivers(site_area, simulation_parameters, grid):
    """

    Generate receiver locations as points within the site area.

    Sampling points can either be generated on a grid (grid=1)
    or more efficiently between the transmitter and the edge
    of the site (grid=0) area.

    Parameters
    ----------
    site_area : polygon
        Shape of the site area we want to generate receivers within.
    simulation_parameters : dict
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
                            "misc_losses": simulation_parameters['rx_misc_losses'],
                            "gain": simulation_parameters['rx_gain'],
                            "losses": simulation_parameters['rx_losses'],
                            "ue_height": float(simulation_parameters['rx_height']),
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

        indoor = simulation_parameters['indoor_users_percentage'] / 100

        id_number = 0
        for increment_value in range(1, 11):
            point = path.interpolate(increment * increment_value)
            indoor_outdoor_probability = np.random.rand(1,1)[0][0]
            receivers.append({
                'type': "Feature",
                'geometry': mapping(point),
                'properties': {
                    'ue_id': "id_{}".format(id_number),
                    "misc_losses": simulation_parameters['rx_misc_losses'],
                    "gain": simulation_parameters['rx_gain'],
                    "losses": simulation_parameters['rx_losses'],
                    "ue_height": float(simulation_parameters['rx_height']),
                    "indoor": (True if float(indoor_outdoor_probability) < \
                        float(indoor) else False),
                }
            })
            id_number += 1

    return receivers


def obtain_average_values(results, simulation_parameters):
    """

    Get the average value for each metric.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    average_site_results : dict
        Contains the average value for each site metric.

    """
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

    average_site_results = {
        'results_type': 'mean',
        'path_loss': get_average(path_loss_values),
        'received_power': get_average(received_power_values),
        'interference': get_average(interference_values),
        'sinr': get_average(sinr_values),
        'spectral_efficiency': get_average(spectral_efficiency_values),
        'capacity_mbps': get_average(estimated_capacity_values),
        'capacity_mbps_km2': get_average(estimated_capacity_values_km2),
    }

    return average_site_results


def get_average(data):
    """

    Simple function to return the average of a list of values.

    Parameters
    ----------
    data : list
        Contains the list of values we want to average.

    Output
    ------
    average : float
        The average value based on the input list of values.

    """
    average = sum(data) / len(data)

    return average


def obtain_percentile_values(results, simulation_parameters):
    """

    Get the threshold value for a metric based on a given percentile.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    percentile_site_results : dict
        Contains the percentile value for each site metric.

    """
    percentile = simulation_parameters['percentile']

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


def obtain_threshold_values_choice(results, simulation_parameters):
    """

    Get the threshold capacity based on a given percentile.

    Parameters
    ----------
    results : list of dicts
        All data returned from the system simulation.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    Output
    ------
    matching_result : float
        Contains the chosen percentile value based on the input data.

    """
    sinr_values = []

    percentile = simulation_parameters['percentile']

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
    bandwidth, generation, ant_height, directory, filename,
    simulation_parameters):
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
    ant_height : int
        Height of the transmitters modelled in meters.
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    """
    sectors = simulation_parameters['sectorization']
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
            'ant_height_m',
            'receiver_x',
            'receiver_y',
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
            ant_height,
            row['receiver_x'],
            row['receiver_y'],
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


def write_frequency_lookup_table(results, environment, site_radius,
    frequency, bandwidth, generation, ant_height,
    directory, filename, simulation_parameters):
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
    ant_height : int
        Height of the transmitters modelled in meters.
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    """
    inter_site_distance = site_radius * 2
    site_area_km2 = math.sqrt(3) / 2 * inter_site_distance ** 2 / 1e6
    sites_per_km2 = 1 / site_area_km2

    sectors = simulation_parameters['sectorization']

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
                'ant_height_m',
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
            results['results_type'],
            environment,
            inter_site_distance,
            site_area_km2,
            sites_per_km2,
            frequency,
            bandwidth,
            sectors,
            generation,
            ant_height,
            results['path_loss'],
            results['received_power'],
            results['interference'],
            results['sinr'],
            results['spectral_efficiency'],
            results['capacity_mbps'],
            results['capacity_mbps_km2'] * sectors,
        )
    )

    lut_file.close()



def write_cost_lookup_table(results, environment, site_radius,
    frequency, bandwidth, generation, ant_height,
    directory, filename, simulation_parameters):
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
    ant_height : int
        Height of the transmitters modelled in meters.
    directory : string
        Folder the data will be written to.
    filename : string
        Name of the .csv file.
    simulation_parameters : dict
        Contains all necessary simulation parameters.

    """
    sectors = simulation_parameters['sectorization']

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
                'capacity_mbps',
                'capacity_mbps_km2',
                'strategy',
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
                environment,
                result['inter_site_distance'],
                result['site_area_km2'],
                result['sites_per_km2'],
                result['capacity_mbps'],
                result['capacity_mbps_km2'] * sectors,
                result['strategy'],
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


def write_shapefile(data, directory, filename, crs):
    """

    Write geojson data to shapefile.

    """
    # Translate props to Fiona sink schema
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

    # Write all elements to output file
    with fiona.open(
        os.path.join(directory, filename), 'w',
        driver=sink_driver, crs=sink_crs, schema=sink_schema) as sink:
        for datum in data:
            sink.write(datum)


def run_simulator(simulation_parameters, spectrum_portfolio,
    ant_heights, site_radii, modulation_and_coding_lut, costs):
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
        for site_radius in site_radii[environment]:

            print('--working on {}: {}'.format(environment, site_radius))

            transmitter, interfering_transmitters, site_area, interfering_site_areas = \
                produce_sites_and_site_areas(
                    unprojected_point['geometry']['coordinates'],
                    site_radius,
                    unprojected_crs,
                    projected_crs
                    )

            receivers = generate_receivers(site_area, SIMULATION_PARAMETERS, 1)

            for frequency, bandwidth, generation in spectrum_portfolio:
                for ant_height in ant_heights:

                    MANAGER = SimulationManager(
                        transmitter, interfering_transmitters, receivers,
                        site_area, SIMULATION_PARAMETERS
                        )

                    results = MANAGER.estimate_link_budget(
                        frequency, bandwidth, generation, ant_height,
                        environment,
                        MODULATION_AND_CODING_LUT,
                        SIMULATION_PARAMETERS
                        )

                    folder = os.path.join(BASE_PATH, '..', 'results', 'full_tables')
                    filename = 'full_capacity_lut_{}_{}_{}_{}.csv'.format(
                        environment, site_radius, frequency, ant_height)

                    write_full_results(results, environment, site_radius,
                        frequency, bandwidth, generation, ant_height,
                        folder, filename, simulation_parameters)

                    average_site_results = obtain_average_values(
                        results, simulation_parameters
                        )

                    results_directory = os.path.join(BASE_PATH, '..', 'results')

                    write_frequency_lookup_table(average_site_results, environment,
                        site_radius, frequency, bandwidth, generation,
                        ant_height, results_directory,
                        'average_capacity_lut.csv',
                        simulation_parameters
                    )

                    if frequency == spectrum_portfolio[0][0]:

                        percentile_site_results = obtain_percentile_values(
                            results, simulation_parameters
                        )

                        percentile_site_results = calculate_costs(
                            percentile_site_results, costs, simulation_parameters,
                            site_radius, environment
                        )

                        write_cost_lookup_table(percentile_site_results, environment,
                            site_radius, frequency, bandwidth, generation,
                            ant_height, results_directory,
                            'percentile_{}_capacity_lut.csv'.format(
                                simulation_parameters['percentile']),
                            simulation_parameters
                        )

                    ## write out as shapes, if desired, for debugging purposes
                    geojson_receivers = convert_results_geojson(results)

                    write_shapefile(
                        geojson_receivers, os.path.join(results_directory, 'shapes'),
                        'receivers_{}.shp'.format(site_radius),
                        projected_crs
                        )

                    write_shapefile(
                        transmitter, os.path.join(results_directory, 'shapes'),
                        'transmitter_{}.shp'.format(site_radius),
                        projected_crs
                    )

                    write_shapefile(
                        site_area, os.path.join(results_directory, 'shapes'),
                        'site_area_{}.shp'.format(site_radius),
                        projected_crs
                    )

                    write_shapefile(
                        interfering_transmitters, os.path.join(results_directory, 'shapes'),
                        'interfering_transmitters_{}.shp'.format(site_radius),
                        projected_crs
                    )

                    write_shapefile(
                        interfering_site_areas, os.path.join(results_directory, 'shapes'),
                        'interfering_site_areas_{}.shp'.format(site_radius),
                        projected_crs
                    )


if __name__ == '__main__':

    SIMULATION_PARAMETERS = {
        'iterations': 5,
        'seed_value1': 1,
        'seed_value2': 2,
        'indoor_users_percentage': 50,
        'los_breakpoint_m': 250,
        'tx_baseline_height': 30,
        'tx_upper_height': 40,
        'tx_power': 40,
        'tx_gain': 16,
        'tx_losses': 1,
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
        'overbooking_factor': 50,
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
        (3.5, 40, '5G'),
        (26, 100, '5G'),
    ]

    ANT_HEIGHT = [
        (30),
        # (40)
    ]

    MODULATION_AND_CODING_LUT =[
        # ETSI. 2018. ‘5G; NR; Physical Layer Procedures for Data
        # (3GPP TS 38.214 Version 15.3.0 Release 15)’. Valbonne, France: ETSI.
        # CQI Index	Modulation	Coding rate
        # Spectral efficiency (bps/Hz) SINR estimate (dB)
        ('4G', 1, 'QPSK', 78,	0.1523, -6.7),
        ('4G', 2, 'QPSK', 120, 0.2344, -4.7),
        ('4G', 3, 'QPSK', 193, 0.377, -2.3),
        ('4G', 4, 'QPSK', 308, 0.6016, 0.2),
        ('4G', 5, 'QPSK', 449, 0.877, 2.4),
        ('4G', 6, 'QPSK', 602, 1.1758, 4.3),
        ('4G', 7, '16QAM', 378, 1.4766, 5.9),
        ('4G', 8, '16QAM', 490, 1.9141, 8.1),
        ('4G', 9, '16QAM', 616, 2.4063, 10.3),
        ('4G', 10, '64QAM', 466, 2.7305, 11.7),
        ('4G', 11, '64QAM', 567, 3.3223, 14.1),
        ('4G', 12, '64QAM', 666, 3.9023, 16.3),
        ('4G', 13, '64QAM', 772, 4.5234, 18.7),
        ('4G', 14, '64QAM', 973, 5.1152, 21),
        ('4G', 15, '64QAM', 948, 5.5547, 22.7),
        ('5G', 1, 'QPSK', 78, 0.1523, -6.7),
        ('5G', 2, 'QPSK', 193, 0.377, -4.7),
        ('5G', 3, 'QPSK', 449, 0.877, -2.3),
        ('5G', 4, '16QAM', 378, 1.4766, 0.2),
        ('5G', 5, '16QAM', 490, 1.9141, 2.4),
        ('5G', 6, '16QAM', 616, 2.4063, 4.3),
        ('5G', 7, '64QAM', 466, 2.7305, 5.9),
        ('5G', 8, '64QAM', 567, 3.3223, 8.1),
        ('5G', 9, '64QAM', 666, 3.9023, 10.3),
        ('5G', 10, '64QAM', 772, 4.5234, 11.7),
        ('5G', 11, '64QAM', 873, 5.1152, 14.1),
        ('5G', 12, '256QAM', 711, 5.5547, 16.3),
        ('5G', 13, '256QAM', 797, 6.2266, 18.7),
        ('5G', 14, '256QAM', 885, 6.9141, 21),
        ('5G', 15, '256QAM', 948, 7.4063, 22.7),
    ]

    def generate_site_radii(min, max, increment):
        for n in range(min, max, increment):
            yield n

    INCREMENT = (200, 5800, 200)

    SITE_RADII = {
        'urban':
            generate_site_radii(INCREMENT[0],INCREMENT[1],INCREMENT[2]),
        'suburban':
            generate_site_radii(INCREMENT[0],INCREMENT[1],INCREMENT[2]),
        'rural':
            generate_site_radii(INCREMENT[0],INCREMENT[1],INCREMENT[2])
        }

    run_simulator(
        SIMULATION_PARAMETERS,
        SPECTRUM_PORTFOLIO,
        ANT_HEIGHT,
        SITE_RADII,
        MODULATION_AND_CODING_LUT,
        COSTS
        )
