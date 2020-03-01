#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

import pytest
from pytest import fixture
from shapely.geometry import Point, LineString, shape, mapping
import os
from collections import OrderedDict
from pysim5g.system_simulator import SimulationManager


@pytest.fixture
def rootdir():
    return os.path.dirname(os.path.abspath(__file__))


@fixture(scope='function')
def setup_transmitter():
    return [{
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': (538742.784267504, 177200.33865700618)
        },
        'properties': {
            'site_id': 'transmitter'
            }
        }]


@fixture(scope='function')
def setup_interfering_transmitters():
    return [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538992.784267504, 176767.32595511398)},
            'properties': {
                'site_id': 5
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538242.784267504, 177200.33865700618)
            },
            'properties': {
                'site_id': 8
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (539242.784267504, 177200.33865700618)
            },
            'properties': {
                'site_id': 10
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538992.784267504, 177633.35135889842)
            },
            'properties': {
                'site_id': 13
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538492.7842675039, 176767.32595511398)
            },
            'properties': {
                'site_id': 4
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538492.7842675039, 177633.35135889842)
            },
            'properties': {
                'site_id': 12
            }
        }
    ]


@fixture(scope='function')
def setup_site_area():
    return [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        (538492.784267504, 177056.00108970876),
                        (538492.784267504, 177344.67622430358),
                        (538742.784267504, 177489.013791601),
                        (538992.784267504, 177344.67622430358),
                        (538992.784267504, 177056.00108970876),
                        (538742.784267504, 176911.66352241137),
                        (538492.784267504, 177056.00108970876)
                    ]
                ]
            },
            'properties': {
                'site_id': 9
            }
        }
    ]


@fixture(scope='function')
def setup_interfering_site_areas():
    return [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    (538742.784267504, 176622.98838781656),
                    (538742.784267504, 176911.66352241137),
                    (538992.784267504, 177056.0010897088),
                    (539242.784267504, 176911.66352241137),
                    (539242.784267504, 176622.98838781656),
                    (538992.784267504, 176478.65082051916),
                    (538742.784267504, 176622.98838781656)]]
                },
            'properties': {'site_id': 5}},
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    (537992.784267504, 177056.00108970876),
                    (537992.784267504, 177344.67622430358),
                    (538242.784267504, 177489.013791601),
                    (538492.784267504, 177344.67622430358),
                    (538492.784267504, 177056.00108970876),
                    (538242.784267504, 176911.66352241137),
                    (537992.784267504, 177056.00108970876)]]
                },
            'properties': {'site_id': 8}},
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    (538992.784267504, 177056.00108970876),
                    (538992.784267504, 177344.67622430358),
                    (539242.784267504, 177489.013791601),
                    (539492.784267504, 177344.67622430358),
                    (539492.784267504, 177056.00108970876),
                    (539242.784267504, 176911.66352241137),
                    (538992.784267504, 177056.00108970876)]]
                },
            'properties': {'site_id': 10}},
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    (538742.784267504, 177489.01379160097),
                    (538742.784267504, 177777.68892619578),
                    (538992.784267504, 177922.0264934932),
                    (539242.784267504, 177777.68892619578),
                    (539242.784267504, 177489.01379160097),
                    (538992.784267504, 177344.67622430358),
                    (538742.784267504, 177489.01379160097)]]
                },
            'properties': {'site_id': 13}},
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    (538242.784267504, 176622.98838781656),
                    (538242.784267504, 176911.66352241137),
                    (538492.784267504, 177056.0010897088),
                    (538742.784267504, 176911.66352241137),
                    (538742.784267504, 176622.98838781656),
                    (538492.784267504, 176478.65082051916),
                    (538242.784267504, 176622.98838781656)]]
                },
            'properties': {'site_id': 4}},
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    (538242.784267504, 177489.01379160097),
                    (538242.784267504, 177777.68892619578),
                    (538492.784267504, 177922.0264934932),
                    (538742.784267504, 177777.68892619578),
                    (538742.784267504, 177489.01379160097),
                    (538492.784267504, 177344.67622430358),
                    (538242.784267504, 177489.01379160097)]]
                },
            'properties': {'site_id': 12}
        }
    ]


@fixture(scope='function')
def setup_receivers():
    return [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538504.908623157, 177063.00108970876)
            },
            'properties': {
                'ue_id': 'id_0',
                'misc_losses': 4,
                'gain': 4,
                'losses': 4,
                'ue_height': 1.5,
                'indoor': True
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538517.03297881, 177070.00108970876)
            },
            'properties': {
                'ue_id': 'id_1',
                'misc_losses': 4,
                'gain': 4,
                'losses': 4,
                'ue_height': 1.5,
                'indoor': False
            }
        },
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': (538529.157334463, 177077.00108970876)
            },
            'properties': {
                'ue_id': 'id_2',
                'misc_losses': 4,
                'gain': 4,
                'losses': 4,
                'ue_height': 1.5,
                'indoor': False
            }
        }
    ]


@fixture(scope='function')
def setup_modulation_coding_lut():
    return [
        #CQI Index	Modulation	Coding rate	Spectral efficiency (bps/Hz) SINR estimate (dB)
        ('4G', '1x1', 1, 'QPSK',	0.0762,	0.1523, -6.7),
        ('4G', '1x1', 2, 'QPSK',	0.1172,	0.2344, -4.7),
        ('4G', '1x1', 3, 'QPSK',	0.1885,	0.377, -2.3),
        ('4G', '1x1', 4, 'QPSK',	0.3008,	0.6016, 0.2),
        ('4G', '1x1', 5, 'QPSK',	0.4385,	0.877, 2.4),
        ('4G', '1x1', 6, 'QPSK',	0.5879,	1.1758,	4.3),
        ('4G', '1x1', 7, '16QAM', 0.3691, 1.4766, 5.9),
        ('4G', '1x1', 8, '16QAM', 0.4785, 1.9141, 8.1),
        ('4G', '1x1', 9, '16QAM', 0.6016, 2.4063, 10.3),
        ('4G', '1x1', 10, '64QAM', 0.4551, 2.7305, 11.7),
        ('4G', '1x1', 11, '64QAM', 0.5537, 3.3223, 14.1),
        ('4G', '1x1', 12, '64QAM', 0.6504, 3.9023, 16.3),
        ('4G', '1x1', 13, '64QAM', 0.7539, 4.5234, 18.7),
        ('4G', '1x1', 14, '64QAM', 0.8525, 5.1152, 21),
        ('4G', '1x1', 15, '64QAM', 0.9258, 5.5547, 22.7),
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
        ]


@pytest.fixture
def setup_parameters():
    return  {
        'iterations': 5,
        'seed_value1': 1,
        'seed_value2': 2,
        'indoor_users_percentage': 50,
        'los_breakpoint_m': 250,
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
        'percentile': 10,
        'sectorization': 3,
        #'overbooking_factor': 50,
        'mnos': 2,
        'asset_lifetime': 10,
        'discount_rate': 3.5,
        'opex_percentage_of_capex': 10,
    }



@pytest.fixture
def base_system(setup_transmitter, setup_interfering_transmitters,
        setup_ant_type, setup_receivers,
        setup_site_area, setup_parameters):

    system = SimulationManager(setup_transmitter,
        setup_interfering_transmitters, setup_ant_type,
        setup_receivers,
        setup_site_area, setup_parameters)

    return system


@pytest.fixture
def setup_unprojected_point():
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': (0, 51.476),
            },
        'properties': {
            'site_id': 'Crystal Palace Radio Tower'
            }
    }


@pytest.fixture
def setup_inter_site_distance():
    return [
        250,
        15000,
    ]


@pytest.fixture
def setup_unprojected_crs():
    return 'epsg:4326'


@pytest.fixture
def setup_projected_crs():
    return 'epsg:3857'


@pytest.fixture
def setup_data():
    return {
        'results_type': '10_percentile',
        'transmission_type': '1x1',
        'path_loss': 96.85199999999999,
        'received_power': -54.666999999999994,
        'interference': -62.08299998089783,
        'sinr': 2.1870000000000003,
        'spectral_efficiency': 1.4766,
        'capacity_mbps': 14.766,
        'capacity_mbps_km2': 68.20123259882035
    }


@pytest.fixture
def setup_costs():
    return {
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


@pytest.fixture
def setup_site_radius():
    return 250


@pytest.fixture
def setup_environment():
    return 'urban'


@pytest.fixture
def setup_ant_type():
    return 'macro'


@pytest.fixture
def setup_transmission_type():
    return '1x1'
