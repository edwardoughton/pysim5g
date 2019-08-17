import pytest
import os
import numpy as np
from shapely.geometry import shape, Point


def test_simulation_manager(base_system, setup_transmitter, setup_site_area):

    assert base_system.transmitter.id == setup_transmitter[0]['properties']['site_id']
    assert base_system.site_area.id == setup_site_area[0]['properties']['site_id']
    assert len(base_system.receivers) == 3
    assert len(base_system.interfering_transmitters) == 6


def test_estimate_link_budget(base_system, setup_modulation_coding_lut,
    setup_simulation_parameters):

    actual_result = base_system.estimate_link_budget(
        0.7, 10, '5G', 30, 'urban', setup_modulation_coding_lut,
        setup_simulation_parameters
        )

    for receiver in actual_result:
        if receiver['id'] == 'id_0':
            assert round(actual_result[0]['path_loss'], 2) == 108.99
            assert round(actual_result[0]['received_power'], 2) == -57.99
            assert round(actual_result[0]['sinr'], 2) == 1.87
            assert round(actual_result[0]['capacity_mbps'], 2) == 14.77
            assert round(actual_result[0]['capacity_mbps_km2'], 2) == 68.2
