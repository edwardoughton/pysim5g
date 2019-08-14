import pytest
from pysim5g.costs import calculate_costs

def test_calculate_costs(setup_data, setup_costs, setup_simulation_parameters,
    setup_site_radius, setup_environment):

    percentile_site_results = calculate_costs(
        setup_data, setup_costs, setup_simulation_parameters,
        setup_site_radius, setup_environment
    )

    assert round(percentile_site_results['sector_antenna_costs_km2']) == 20785
    assert round(percentile_site_results['remote_radio_unit_costs_km2']) == 55426
    assert round(percentile_site_results['baseband_unit_costs_km2']) == 46188
    assert round(percentile_site_results['router_costs_km2']) == 9238
    assert round(percentile_site_results['tower_costs_km2']) == 46188
    assert round(percentile_site_results['civil_material_costs_km2']) == 23094
    assert round(percentile_site_results['transportation_costs_km2']) == 46188
    assert round(percentile_site_results['installation_costs_km2']) == 23094
    assert round(percentile_site_results['battery_system_costs_km2']) == 36950
    assert round(percentile_site_results['fiber_backhaul_costs_km2']) ==  69282
    assert round(percentile_site_results['microwave_backhaul_1m_costs_km2']) == 18475
