import pytest
from pysim5g.costs import calculate_costs
from pysim5g.costs import discount_cost

def test_calculate_costs(setup_data, setup_costs, setup_parameters,
    setup_site_radius, setup_environment):

    percentile_site_results = calculate_costs(
        setup_data, setup_costs, setup_parameters,
        setup_site_radius, setup_environment
    )

    baseline_results = []
    for result in percentile_site_results:
        if result['strategy'] == 'baseline':
            baseline_results.append(result)

    assert round(baseline_results[0]['sector_antenna_costs_km2']) == 38675
    assert round(baseline_results[0]['remote_radio_unit_costs_km2']) == 103134
    assert round(baseline_results[0]['baseband_unit_costs_km2']) == 85945
    assert round(baseline_results[0]['tower_costs_km2']) == 46188
    assert round(baseline_results[0]['civil_material_costs_km2']) == 23094
    assert round(baseline_results[0]['transportation_costs_km2']) == 46188
    assert round(baseline_results[0]['installation_costs_km2']) == 23094
    assert round(baseline_results[0]['site_rental_km2']) == 381669
    assert round(baseline_results[0]['power_system_costs_km2']) == 42973
    assert round(baseline_results[0]['fiber_backhaul_costs_km2']) ==  128918
    assert round(baseline_results[0]['router_costs_km2']) == 17189

    passive_site_sharing = []
    for result in percentile_site_results:
        if result['strategy'] == 'passive_site_sharing':
            passive_site_sharing.append(result)

    assert round(passive_site_sharing[0]['sector_antenna_costs_km2']) == 38675
    assert round(passive_site_sharing[0]['remote_radio_unit_costs_km2']) == 103134
    assert round(passive_site_sharing[0]['baseband_unit_costs_km2']) == 85945
    assert round(passive_site_sharing[0]['tower_costs_km2']) == 23094
    assert round(passive_site_sharing[0]['civil_material_costs_km2']) == 11547
    assert round(passive_site_sharing[0]['transportation_costs_km2']) == 23094
    assert round(passive_site_sharing[0]['installation_costs_km2']) == 11547
    assert round(passive_site_sharing[0]['site_rental_km2']) == 190835
    assert round(passive_site_sharing[0]['power_system_costs_km2']) == 21486
    assert round(passive_site_sharing[0]['fiber_backhaul_costs_km2']) ==  128918
    assert round(passive_site_sharing[0]['router_costs_km2']) == 17189

    passive_backhaul_sharing = []
    for result in percentile_site_results:
        if result['strategy'] == 'passive_backhaul_sharing':
            passive_backhaul_sharing.append(result)

    assert round(passive_backhaul_sharing[0]['sector_antenna_costs_km2']) == 38675
    assert round(passive_backhaul_sharing[0]['remote_radio_unit_costs_km2']) == 103134
    assert round(passive_backhaul_sharing[0]['baseband_unit_costs_km2']) == 85945
    assert round(passive_backhaul_sharing[0]['tower_costs_km2']) == 46188
    assert round(passive_backhaul_sharing[0]['civil_material_costs_km2']) == 23094
    assert round(passive_backhaul_sharing[0]['transportation_costs_km2']) == 46188
    assert round(passive_backhaul_sharing[0]['installation_costs_km2']) == 23094
    assert round(passive_backhaul_sharing[0]['site_rental_km2']) == 190835
    assert round(passive_backhaul_sharing[0]['power_system_costs_km2']) == 21486
    assert round(passive_backhaul_sharing[0]['fiber_backhaul_costs_km2']) ==  64459
    assert round(passive_backhaul_sharing[0]['router_costs_km2']) == 8595

    active_moran = []
    for result in percentile_site_results:
        if result['strategy'] == 'active_moran':
            active_moran.append(result)

    assert round(active_moran[0]['sector_antenna_costs_km2']) == 19338
    assert round(active_moran[0]['remote_radio_unit_costs_km2']) == 51567
    assert round(active_moran[0]['baseband_unit_costs_km2']) == 42973
    assert round(active_moran[0]['tower_costs_km2']) == 23094
    assert round(active_moran[0]['civil_material_costs_km2']) == 11547
    assert round(active_moran[0]['transportation_costs_km2']) == 23094
    assert round(active_moran[0]['installation_costs_km2']) == 11547
    assert round(active_moran[0]['site_rental_km2']) == 190835
    assert round(active_moran[0]['power_system_costs_km2']) == 21486
    assert round(active_moran[0]['fiber_backhaul_costs_km2']) ==  64459
    assert round(active_moran[0]['router_costs_km2']) == 8595


def test_discount_cost(setup_parameters):

    actual_result = round(discount_cost(1500, setup_parameters, 1))

    #capex == 1500
    #opex == 1291
    total_cost_of_ownership = 2791

    assert actual_result == total_cost_of_ownership
