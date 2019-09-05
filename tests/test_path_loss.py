import pytest
from pysim5g.path_loss import (
    path_loss_calculator,
    etsi_tr_138_901,
    uma_nlos_optional,
    check_3gpp_applicability,
    )


#prepare for testing etsi_tr_138_901
@pytest.mark.parametrize("frequency, distance, ant_height, ant_type, \
    building_height, street_width, settlement_type, type_of_sight, \
    ue_height, above_roof, indoor, seed_value, iterations, expected", [
    (0.7,100,35,'macro',5,20,'rural','los',1.5,0,1,42,1,round(70+0.34+0.27)),
    (0.7,5000,35,'macro',5,20,'rural','los',1.5,0,1,42,1,round(121+0.34+0.27)),
    (0.7,100,35,'macro',5,20,'rural','nlos',1.5,0,1,42,1,round(79+0.23)),
    (0.7,5000,35,'macro',5,20,'rural','nlos',1.5,0,1,42,1,round(144+0.23)),
    (3.5,20000,30,'macro',5,20,'urban','nlos',1.5,0,1,42,1,round(172.3+3.26)),

    (0.7,100,35,'macro',5,20,'urban','los',1.5,0,1,42,1,round(69+0.34+0.27)),
    (0.7,5000,35,'macro',5,20,'urban','los',1.5,0,1,42,1,round(133+0.34+0.27)),
    (0.7,100,35,'macro',5,20,'urban','nlos',1.5,0,1,42,1,round(90+0.23)),
    (0.7,5000,35,'macro',5,20,'urban','nlos',1.5,0,1,42,1,round(155+0.27)),
    # (0.7,5000,35,'macro',5,20,'urban','nlos',1.5,0,1,42,1,round(155+0.27)),
    ])


def test_etsi_tr_138_901(frequency, distance, ant_height, ant_type, \
    building_height, street_width, settlement_type, type_of_sight, \
    ue_height, above_roof, indoor, seed_value, iterations, expected):

    assert etsi_tr_138_901(frequency, distance, ant_height, ant_type,
        building_height, street_width, settlement_type, type_of_sight,
        ue_height, above_roof, indoor, seed_value, iterations) == expected


#prepare for testing UMa NLOS optional model
@pytest.mark.parametrize("frequency, distance, ant_height, ue_height, \
    seed_value, iterations, expected", [
    #expected value is: (deterministic path loss, stochastic component)
    (3.5,1000.41,30,1.5,42,1,round((133.29+3.26))),
    (3.5,5000.08,30,1.5,42,1, round((154.25+3.26))),
    (3.5,10000.04,30,1.5,42,1, round((163.28+3.26))),
    (3.5,20000.02,30,1.5,42,1, round((172.31+3.26))),
    ])


def test_uma_nlos_optional(frequency, distance, ant_height, ue_height, seed_value,
    iterations, expected):

    assert (
        uma_nlos_optional(frequency, distance, ant_height, ue_height, seed_value,
        iterations)) == expected


def test_path_loss_calculator_errors():

    with pytest.raises(ValueError, match='frequency of 0.01 is NOT within correct range'):
        path_loss_calculator(
            0.01,500,10,'micro',20,20,'urban','los',1.5,1, True, 42, 1
            )


#Prepare for testing path_loss_calculator
@pytest.mark.parametrize("frequency, distance, ant_height, ant_type, \
    building_height, street_width, settlement_type, type_of_sight, \
    ue_height, above_roof, indoor, seed_value, iterations, expected", [
    (0.7,100,35,'macro',5,20,'rural','los',1.5,0,1,42,1,(round(70+0.34+0.27+2), 'etsi_tr_138_901')),
    (0.7,5000,35,'macro',5,20,'rural','los',1.5,0,1,42,1,(round(121+0.34+0.27+2), 'etsi_tr_138_901')),
    (0.7,100,35,'macro',5,20,'rural','nlos',1.5,0,1,42,1,(round(79+0.23+2), 'etsi_tr_138_901')),
    (0.7,5000,35,'macro',5,20,'rural','nlos',1.5,0,1,42,1,(round(144+0.23+2), 'etsi_tr_138_901')),
    (3.5,20000,30,'macro',5,20,'urban','nlos',1.5,0,1,42,1,(round(172.3+3.26+5), 'etsi_tr_138_901')),

    (0.7,100,35,'macro',5,20,'urban','los',1.5,0,1,42,1,(round(69+0.34+0.27+2), 'etsi_tr_138_901')),
    (0.7,5000,35,'macro',5,20,'urban','los',1.5,0,1,42,1,(round(133+0.34+0.27+2), 'etsi_tr_138_901')),
    (0.7,100,35,'macro',5,20,'urban','nlos',1.5,0,1,42,1,(round(90+2), 'etsi_tr_138_901')),
    (0.7,5000,35,'macro',5,20,'urban','nlos',1.5,0,1,42,1,(round(155+2), 'etsi_tr_138_901')),
    ])


def test_path_loss_calculator(frequency, distance, ant_height, ant_type,
    building_height,street_width, settlement_type, type_of_sight, ue_height,
    above_roof, indoor, seed_value, iterations, expected):

    assert (
        path_loss_calculator(frequency, distance, ant_height, ant_type,
        building_height, street_width, settlement_type, type_of_sight,
        ue_height, above_roof, indoor, seed_value, iterations)
        ) == expected


#Prepare for testing 3GPP compatability function
@pytest.mark.parametrize("building_height, street_width, ant_height, \
    ue_height, expected", [
    (50, 20, 20, 1.5, False),
    (5, 20, 8, 1.5, False),
    (20, 100, 20, 1.5, False),
    (20, 100, 20, 100, False),
    (20, 20, 20, 1.5, True),
    (5, 20, 8, 1.5, False),
    ])


def test_check_applicability(building_height, street_width, ant_height,
    ue_height, expected):
    assert (
        check_3gpp_applicability(building_height, street_width, ant_height,
        ue_height)
        ) == expected
