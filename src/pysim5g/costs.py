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

    for key, value in simulation_parameters.items():
        if key == 'backhaul_distance_km_{}'.format(environment):
            backhaul_distance = value

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

    total_deployment_costs_km2 = 0
    for key, value in cost_breakdown.items():
        total_deployment_costs_km2 += value

    output = {
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
        'total_deployment_costs_km2': total_deployment_costs_km2,
        'sector_antenna_costs_km2': cost_breakdown['single_sector_antenna_2x2_mimo_dual_band'],
        'remote_radio_unit_costs_km2': cost_breakdown['single_remote_radio_unit'],
        'baseband_unit_costs_km2': cost_breakdown['single_baseband_unit'],
        'router_costs_km2': cost_breakdown['router'],
        'tower_costs_km2': cost_breakdown['tower'],
        'civil_material_costs_km2': cost_breakdown['civil_materials'],
        'transportation_costs_km2': cost_breakdown['transportation'],
        'installation_costs_km2': cost_breakdown['installation'],
        'battery_system_costs_km2': cost_breakdown['battery_system'],
        'fiber_backhaul_costs_km2': cost_breakdown['fiber_backhaul_{}'.format(environment)],
        'microwave_backhaul_1m_costs_km2': cost_breakdown['microwave_backhaul_1m'],
    }

    return output
