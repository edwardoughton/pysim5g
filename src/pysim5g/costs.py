"""
Cost module

Author: Edward Oughton
Date: April 2019

"""
import math

def calculate_costs(data, costs, simulation_parameters, site_radius, environment):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    data : list of dicts
        Contains a list of assets
    costs : dict
        Contains the costs of each necessary equipment item.
    site_radius : int
        The radius of the site area being modelled.
    environment : string
        Either urban, suburban or rural.

    Returns
    -------
    output : list of dicts
        Contains a list of assets, with affliated discounted capex and opex costs.

    """
    inter_site_distance = site_radius * 2
    site_area_km2 = math.sqrt(3) / 2 * inter_site_distance ** 2 / 1e6
    sites_per_km2 = 1 / site_area_km2

    sharing_strategies = [
        'baseline',
        'passive_site_sharing',
        'passive_backhaul_sharing',
        'active_moran',
        'active_mocn',
        'active_cn_sharing',
    ]

    output = []

    for strategy in sharing_strategies:
        print('working on {}'.format(strategy))
        for key, value in simulation_parameters.items():
            if key == 'backhaul_distance_km_{}'.format(environment):
                backhaul_distance = value

        cost_breakdown = get_costs(strategy, costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)

        total_deployment_costs_km2 = 0
        for key, value in cost_breakdown.items():
            total_deployment_costs_km2 += value

        output.append(
            {
                'environment': environment,
                'inter_site_distance': inter_site_distance,
                'site_area_km2': site_area_km2,
                'sites_per_km2': sites_per_km2,
                'results_type': data['results_type'],
                'path_loss': data['path_loss'],
                'received_power': data['received_power'],
                'interference': data['interference'],
                'sinr': data['sinr'],
                'spectral_efficiency': data['spectral_efficiency'],
                'capacity_mbps': data['capacity_mbps'],
                'capacity_mbps_km2': data['capacity_mbps'],
                'strategy': strategy,
                'total_deployment_costs_km2': total_deployment_costs_km2,
                'sector_antenna_costs_km2': cost_breakdown['single_sector_antenna_2x2_mimo_dual_band'],
                'remote_radio_unit_costs_km2': cost_breakdown['single_remote_radio_unit'],
                'baseband_unit_costs_km2': cost_breakdown['single_baseband_unit'],
                'router_costs_km2': cost_breakdown['router'],
                'site_rental': cost_breakdown['site_rental'],
                'tower_costs_km2': cost_breakdown['tower'],
                'civil_material_costs_km2': cost_breakdown['civil_materials'],
                'transportation_costs_km2': cost_breakdown['transportation'],
                'installation_costs_km2': cost_breakdown['installation'],
                'battery_system_costs_km2': cost_breakdown['battery_system'],
                'fiber_backhaul_costs_km2': cost_breakdown['fiber_backhaul_{}'.format(environment)],
                'microwave_backhaul_1m_costs_km2': cost_breakdown['microwave_backhaul_1m'],
            }
        )

    return output


def get_costs(strategy, costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):

    if strategy == 'baseline':
        costs = baseline(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)
    if strategy == 'passive_site_sharing':
        costs = compound_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)
    if strategy == 'passive_backhaul_sharing':
        costs = mast_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)
    if strategy == 'active_moran':
        costs = ran_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)
    if strategy == 'active_mocn':
        costs = mast_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)
    if strategy == 'active_cn_sharing':
        costs = ran_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters)

    return costs


def baseline(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):
    """
    No sharing takes place.

    Reflects the baseline scenario of needing to build a single dedicated network.

    """
    cost_breakdown = {
        'single_sector_antenna_2x2_mimo_dual_band': (
            costs['single_sector_antenna_2x2_mimo_dual_band'] *
            simulation_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit'] *
            simulation_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit'] * sites_per_km2
        ),
        'router': (
            costs['router'] * sites_per_km2
        ),
        'site_rental': costs['site_rental'],
        'tower': (
            costs['tower'] * sites_per_km2
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2
        ),
        'installation': (
            costs['installation'] * sites_per_km2
        ),
        'battery_system': (
            costs['battery_system'] * sites_per_km2
        ),
        'fiber_backhaul_{}'.format(environment): (
            costs['fixed_fiber_backhaul_per_km'] * backhaul_distance * sites_per_km2
        ),
        'microwave_backhaul_1m': (
            costs['microwave_backhaul_1m'] * sites_per_km2
        )
    }

    return cost_breakdown


def passive_site_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):
    """
    Sharing of:
        - Site compound

    """
    cost_breakdown = {
        'single_sector_antenna_2x2_mimo_dual_band': (
            costs['single_sector_antenna_2x2_mimo_dual_band'] *
            simulation_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit'] *
            simulation_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit'] * sites_per_km2
        ),
        'router': (
            costs['router'] * sites_per_km2
        ),
        'site_rental': (
            costs['site_rental'] / simulation_parameters['number_of_mnos_sharing']
        ),
        'tower': (
            costs['tower'] * sites_per_km2
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2
        ),
        'installation': (
            costs['installation'] * sites_per_km2
        ),
        'battery_system': (
            costs['battery_system'] * sites_per_km2
        ),
        'fiber_backhaul_{}'.format(environment): (
            costs['fixed_fiber_backhaul_per_km'] * backhaul_distance * sites_per_km2
        ),
        'microwave_backhaul_1m': (
            costs['microwave_backhaul_1m'] * sites_per_km2
        )
    }

    return cost_breakdown


def passive_backhaul_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):
    """
    Sharing of:
        - Site compound
        - Mast

    """
    cost_breakdown = {
        'single_sector_antenna_2x2_mimo_dual_band': (
            costs['single_sector_antenna_2x2_mimo_dual_band'] *
            simulation_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit'] *
            simulation_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit'] * sites_per_km2
        ),
        'router': (
            costs['router'] * sites_per_km2
        ),
        'site_rental': (
            costs['site_rental'] / simulation_parameters['number_of_mnos_sharing']
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'battery_system': (
            costs['battery_system'] * sites_per_km2
        ),
        'fiber_backhaul_{}'.format(environment): (
            costs['fixed_fiber_backhaul_per_km'] * backhaul_distance * sites_per_km2
        ),
        'microwave_backhaul_1m': (
            costs['microwave_backhaul_1m'] * sites_per_km2
        )
    }

    return cost_breakdown


def active_moran(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    cost_breakdown = {
        'single_sector_antenna_2x2_mimo_dual_band': (
            costs['single_sector_antenna_2x2_mimo_dual_band'] *
            simulation_parameters['sectorization'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit'] *
            simulation_parameters['sectorization'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'router': (
            costs['router'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'site_rental': (
            costs['site_rental'] / simulation_parameters['number_of_mnos_sharing']
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'battery_system': (
            costs['battery_system'] * sites_per_km2
        ),
        'fiber_backhaul_{}'.format(environment): (
            costs['fixed_fiber_backhaul_per_km'] * backhaul_distance * sites_per_km2
        ),
        'microwave_backhaul_1m': (
            costs['microwave_backhaul_1m'] * sites_per_km2
        )
    }

    return cost_breakdown



def active_mocn(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    cost_breakdown = {
        'single_sector_antenna_2x2_mimo_dual_band': (
            costs['single_sector_antenna_2x2_mimo_dual_band'] *
            simulation_parameters['sectorization'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit'] *
            simulation_parameters['sectorization'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'router': (
            costs['router'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'site_rental': (
            costs['site_rental'] / simulation_parameters['number_of_mnos_sharing']
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'battery_system': (
            costs['battery_system'] * sites_per_km2
        ),
        'fiber_backhaul_{}'.format(environment): (
            costs['fixed_fiber_backhaul_per_km'] * backhaul_distance * sites_per_km2
        ),
        'microwave_backhaul_1m': (
            costs['microwave_backhaul_1m'] * sites_per_km2
        )
    }

    return cost_breakdown



def active_cn_sharing(costs, sites_per_km2, environment, backhaul_distance, simulation_parameters):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    cost_breakdown = {
        'single_sector_antenna_2x2_mimo_dual_band': (
            costs['single_sector_antenna_2x2_mimo_dual_band'] *
            simulation_parameters['sectorization'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit'] *
            simulation_parameters['sectorization'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'router': (
            costs['router'] * sites_per_km2 /
            simulation_parameters['number_of_mnos_sharing']
        ),
        'site_rental': (
            costs['site_rental'] / simulation_parameters['number_of_mnos_sharing']
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / simulation_parameters['number_of_mnos_sharing']
        ),
        'battery_system': (
            costs['battery_system'] * sites_per_km2
        ),
        'fiber_backhaul_{}'.format(environment): (
            costs['fixed_fiber_backhaul_per_km'] * backhaul_distance * sites_per_km2
        ),
        'microwave_backhaul_1m': (
            costs['microwave_backhaul_1m'] * sites_per_km2
        )
    }

    return cost_breakdown
