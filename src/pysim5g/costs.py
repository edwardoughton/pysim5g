"""
Cost module

Author: Edward Oughton
Date: April 2019

"""
import math

def calculate_costs(datum, costs, parameters, site_radius, environment):
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
    ]

    output = []

    for strategy in sharing_strategies:

        print('working on {}'.format(strategy))

        cost_breakdown = get_costs(strategy, costs, sites_per_km2, environment, parameters)

        total_deployment_costs_km2 = 0
        for key, value in cost_breakdown.items():
            total_deployment_costs_km2 += value

        output.append({
                'results_type': datum['results_type'],
                'environment': environment,
                'inter_site_distance': inter_site_distance,
                'site_area_km2': site_area_km2,
                'sites_per_km2': sites_per_km2,
                'tranmission_type': datum['tranmission_type'],
                'results_type': 'percentile_{}'.format(parameters['percentile']),
                'path_loss': datum['path_loss'],
                'received_power': datum['received_power'],
                'interference': datum['interference'],
                'sinr': datum['sinr'],
                'spectral_efficiency': datum['spectral_efficiency'],
                'capacity_mbps': datum['capacity_mbps'],
                'capacity_mbps_km2': datum['capacity_mbps'],
                'strategy': strategy,
                'total_deployment_costs_km2': total_deployment_costs_km2,
                'sector_antenna_costs_km2': cost_breakdown['single_sector_antenna'],
                'remote_radio_unit_costs_km2': cost_breakdown['single_remote_radio_unit'],
                'baseband_unit_costs_km2': cost_breakdown['single_baseband_unit'],
                'site_rental_km2': cost_breakdown['site_rental'],
                'tower_costs_km2': cost_breakdown['tower'],
                'civil_material_costs_km2': cost_breakdown['civil_materials'],
                'transportation_costs_km2': cost_breakdown['transportation'],
                'installation_costs_km2': cost_breakdown['installation'],
                'power_system_costs_km2': cost_breakdown['power_generator_battery_system'],
                'fiber_backhaul_costs_km2': cost_breakdown['high_speed_backhaul_hub'],
                'router_costs_km2': cost_breakdown['router'],
            })

    return output


def get_costs(strategy, costs, sites_per_km2, environment, parameters):

    if strategy == 'baseline':
        costs = baseline(costs, sites_per_km2, environment, parameters)
    if strategy == 'passive_site_sharing':
        costs = passive_site_sharing(costs, sites_per_km2, environment, parameters)
    if strategy == 'passive_backhaul_sharing':
        costs = passive_backhaul_sharing(costs, sites_per_km2, environment, parameters)
    if strategy == 'active_moran':
        costs = active_moran(costs, sites_per_km2, environment, parameters)

    return costs


def baseline(costs, sites_per_km2, environment, parameters):
    """
    No sharing takes place.

    Reflects the baseline scenario of needing to build a single dedicated network.

    """
    cost_breakdown = {
        'single_sector_antenna': (
            discount_cost(costs['single_sector_antenna'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_cost(costs['single_remote_radio_unit'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_cost(costs['single_baseband_unit'], parameters, 1) *
            sites_per_km2
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
        'site_rental': (
            discount_cost(costs['site_rental'], parameters, 0) * sites_per_km2
        ),
        'power_generator_battery_system': (
            discount_cost(costs['power_generator_battery_system'], parameters, 1) *
            sites_per_km2
        ),
        'high_speed_backhaul_hub': (
            discount_cost(costs['high_speed_backhaul_hub'], parameters, 1) *
            sites_per_km2
        ),
        'router': (
            discount_cost(costs['router'], parameters, 1) * sites_per_km2
        )
    }

    return cost_breakdown


def passive_site_sharing(costs, sites_per_km2, environment, parameters):
    """
    Sharing of:
        - Site compound

    """
    cost_breakdown = {
        'single_sector_antenna': (
            discount_cost(costs['single_sector_antenna'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_cost(costs['single_remote_radio_unit'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_cost(costs['single_baseband_unit'], parameters, 1) *
            sites_per_km2
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / parameters['mnos']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / parameters['mnos']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / parameters['mnos']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / parameters['mnos']
        ),
        'site_rental': (
            discount_cost(costs['site_rental'], parameters, 0) *
            sites_per_km2 / parameters['mnos']
        ),
        'power_generator_battery_system': (
            discount_cost(costs['power_generator_battery_system'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        ),
        'high_speed_backhaul_hub': (
            discount_cost(costs['high_speed_backhaul_hub'], parameters, 1) *
            sites_per_km2
        ),
        'router': (
            discount_cost(costs['router'], parameters, 1) *
            sites_per_km2
        )
    }

    return cost_breakdown


def passive_backhaul_sharing(costs, sites_per_km2, environment, parameters):
    """
    Sharing of:
        - Site compound
        - Mast

    """
    cost_breakdown = {
        'single_sector_antenna': (
            discount_cost(costs['single_sector_antenna'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_cost(costs['single_remote_radio_unit'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_cost(costs['single_baseband_unit'], parameters, 1) *
            sites_per_km2
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
        'site_rental': (
            discount_cost(costs['site_rental'], parameters, 0) *
            sites_per_km2 / parameters['mnos']
        ),
        'power_generator_battery_system': (
            discount_cost(costs['power_generator_battery_system'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        ),
        'high_speed_backhaul_hub': (
            discount_cost(costs['high_speed_backhaul_hub'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        ),
        'router': (
            discount_cost(costs['router'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        )
    }

    return cost_breakdown


def active_moran(costs, sites_per_km2, environment, parameters):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    cost_breakdown = {
        'single_sector_antenna': (
            discount_cost(costs['single_sector_antenna'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2 /
            parameters['mnos']
        ),
        'single_remote_radio_unit': (
            discount_cost(costs['single_remote_radio_unit'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2 /
            parameters['mnos']
        ),
        'single_baseband_unit': (
            discount_cost(costs['single_baseband_unit'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        ),
        'tower': (
            costs['tower'] *
            sites_per_km2 / parameters['mnos']
        ),
        'civil_materials': (
            costs['civil_materials'] *
            sites_per_km2 / parameters['mnos']
        ),
        'transportation': (
            costs['transportation'] *
            sites_per_km2 / parameters['mnos']
        ),
        'installation': (
            costs['installation'] *
            sites_per_km2 / parameters['mnos']
        ),
        'site_rental': (
            discount_cost(costs['site_rental'], parameters, 0) *
            sites_per_km2 / parameters['mnos']
        ),
        'power_generator_battery_system': (
            discount_cost(costs['power_generator_battery_system'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        ),
        'high_speed_backhaul_hub': (
            discount_cost(costs['high_speed_backhaul_hub'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        ),
        'router': (
            discount_cost(costs['router'], parameters, 1) *
            sites_per_km2 / parameters['mnos']
        )
    }

    return cost_breakdown


def discount_cost(cost, parameters, capex):
    """
    Discount costs based on asset_lifetime.

    """
    asset_lifetime = parameters['asset_lifetime']
    discount_rate = parameters['discount_rate'] / 100

    if capex == 1:
        capex = cost

        opex = round(capex * (parameters['opex_percentage_of_capex'] / 100))

        total_cost_of_ownership = 0
        total_cost_of_ownership += capex

        for i in range(0, asset_lifetime ):
            total_cost_of_ownership += (
                opex / (1 + discount_rate) ** i
            )
    else:
        opex = cost
        total_cost_of_ownership = 0

        for i in range(0, asset_lifetime ):
            total_cost_of_ownership += (
                opex / (1 + discount_rate) ** i
            )

    return total_cost_of_ownership
