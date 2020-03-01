import pytest
import os
import numpy as np
from shapely.geometry import shape, Point


def test_simulation_manager(base_system, setup_transmitter, setup_ant_type, setup_site_area):

    assert base_system.transmitter.id == setup_transmitter[0]['properties']['site_id']
    assert base_system.site_area.id == setup_site_area[0]['properties']['site_id']
    assert len(base_system.receivers) == 3
    assert len(base_system.interfering_transmitters) == 6


def test_estimate_link_budget(base_system, setup_modulation_coding_lut,
    setup_parameters):

    actual_result = base_system.estimate_link_budget(
        0.7, 10, '5G', 'macro', '1x1', 'urban', setup_modulation_coding_lut,
        setup_parameters
        )

    for receiver in actual_result:
        if receiver['id'] == 'id_0':
            assert round(actual_result[0]['path_loss']) == 110
            assert round(actual_result[0]['received_power']) == -59
            assert round(actual_result[0]['sinr']) == 3
            assert round(actual_result[0]['capacity_mbps']) == 19
            assert round(actual_result[0]['capacity_mbps_km2']) == 88
