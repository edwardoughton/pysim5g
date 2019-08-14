import pytest
from pysim5g.path_loss import (
    path_loss_calculator,
    determine_path_loss,
    free_space,
    extended_hata,
    uma_nlos_optional,
    )


#prepare for testing Free Space model
@pytest.mark.parametrize("frequency, distance, ant_height, ue_height, \
    seed_value, iterations, expected", [

    #expected value is: (deterministic path loss, stochastic component)
    (0.8,1000,20,1.5,42,1,round(90.46+0.48,2)),
    (0.8,2000,20,1.5,42,1,round(96.48+0.48,2)),
    (0.8,3000,20,1.5,42,1,round(100+0.48,2)),
    (0.8,4000,20,1.5,42,1,round(102.5+0.48,2)),
    (0.8,5000,20,1.5,42,1,round(104.44+0.48,2)),
    (1.8,1000,20,1.5,42,1,round(97.51+0.34,2)),
    (1.8,2000,20,1.5,42,1,round(103.53+0.34,2)),
    (1.8,3000,20,1.5,42,1,round(107.05+0.34,2)),
    (1.8,4000,20,1.5,42,1,round(109.55+0.34,2)),
    (1.8,5000,20,1.5,42,1,round(111.48+0.34,2)),
    (2.6,1000,20,1.5,42,1,round(100.7+2.24,2)),
    (2.6,2000,20,1.5,42,1,round(106.72+2.24,2)),
    (2.6,3000,20,1.5,42,1,round(110.24+2.24,2)),
    (2.6,4000,20,1.5,42,1,round(112.74+2.24,2)),
    (2.6,5000,20,1.5,42,1,(round(114.68+2.24,2))),
    ])


def test_free_space(frequency, distance, ant_height, ue_height, seed_value,
    iterations, expected):

    assert (
        free_space(frequency, distance, ant_height, ue_height, seed_value,
        iterations)
        ) == expected


### prepare for testing Extended HATA model
@pytest.mark.parametrize("frequency, distance, ant_height, ant_type, \
    building_height, street_width, settlement_type, type_of_sight, \
    ue_height, above_roof, seed_value, iterations, expected", [
    ###urban####
    # test distance <0.04 km
    (0.8,20,20,'macro',20,20,'urban','los',1.5,1,42,1,(59.17+0.41)),
    # test distance <0.04 km, above roof
    (0.1,200,20,'macro',20,20,'urban','los',1.5,1,42,1,round(81.65+0.7,2)),
    # test distance >0.04 km, below roof
    (0.1,200,20,'',20,20,'urban','nlos',1.5,0,42,1,round(81.65+0.64,2)),
    # # test distance >0.04 km, above roof
    (0.8,200,20,'',20,20,'urban','los',1.5,1,42,1,round(104.14+0.21,2)),
    # # test distance >0.04 km, below roof
    (0.8,200,20,'',20,20,'urban','nlos',1.5,0,42,1,round(104.14+0.18,2)),
    # # test distance >0.04 km, above roof
    (1.8,200,20,'',20,20,'urban','los',1.5,1,42,1,round(115.10+0.12,2)),
    # # test distance >0.04 km, below roof
    (1.8,200,20,'',20,20,'urban','nlos',1.5,0,42,1,(round(115.10+0.1,2))),
    # # test distance >0.04 km, above roof
    (2.1,200,20,'',20,20,'urban','los',1.5,1,42,1,round(116.85+0.4,2)),
    # # test distance >0.04 km, below roof
    (2.1,200,20,'',20,20,'urban','nlos',1.5,0,42,1,(round(116.85+0.35,2))),
    # ####suburban####
    # # test distance >0.04 km, above roof
    (0.8,200,20,'',20,20,'suburban','los',1.5,1,42,1,round(94.50+0.21,2)),
    # # test distance >0.04 km, below roof
    (0.8,200,20,'',20,20,'suburban','nlos',1.5,0,42,1,round(94.50+0.18,2)),
    # # test distance 0.5 km, above roof
    (0.8,500,20,'',20,20,'suburban','los',1.5,1,42,1,(round(108.51+0.24,2))),
    # # test distance 0.5 km, above roof
    (0.8,500,20,'',20,20,'suburban','los',1.5,0,42,1,(round(108.51+0.27,2))),
    # ####rural####
    # # test distance >0.04 km, above roof
    (1.8,200,20,'',20,20,'rural','los',1.5,1,42,1,(83.17+0.12)),
    # #####test 500m####
    # # test distance 0.05 km, above roof
    (1.8,500,20,'',20,20,'urban','los',1.5,1,42,1,(round(129.12+0.14,2))),
    # # test distance 0.05 km, below roof
    (1.8,500,20,'',20,20,'urban','nlos',1.5,0,42,1,(129.12+0.16)),
    # #change distances
    # #test 90m (0.04< d <0.1)
    # # test distance 0.09 km, above roof
    (1.8,90,20,'',20,20,'urban','los',1.5,1,42,1,(round(76.82+0.16,2))),
    # # test distance 0.09 km, below roof
    (1.8,90,20,'',20,20,'urban','nlos',1.5,0,42,1,(round(76.82+0.13,2))),
    # #test 5km
    # # test distance 5 km, above roof
    (1.8,5000,20,'',20,20,'urban','los',1.5,1,42,1,(164.34+0.12)),
    # # test distance 5 km, above roof
    (1.8,5000,20,'',20,20,'rural','los',1.5,1,42,1,(round(132.42+0.12,2))),
    # #test 20km
    # # test distance 20 km, above roof
    (0.7,20000,20,'',20,20,'urban','los',1.5,1,42,1,(round(173.07+0.18,2))),
    (0.7,20000,20,'',20,20,'rural','los',1.5,1,42,1,(round(145.59+0.18,2))),
    # #test 21km
    # # test distance 21 km, above roof
    (0.7,21000,20,'',20,20,'urban','los',1.5,1,42,1,round(173.99+0.18,2)),
    (0.7,21000,20,'',20,20,'rural','los',1.5,1,42,1,(round(146.51+0.18,2))),
    # # test distance 25 km, above roof
    (0.7,25000,20,'',20,20,'urban','los',1.5,1,42,1,round(177.24+0.18,2)),
    (0.7,25000,20,'',20,20,'rural','los',1.5,1,42,1,(round(149.76+0.18,2))),
    # #test 50km
    # # test distance 50 km, above roof
    (0.7,50000,20,'',20,20,'urban','los',1.5,1,42,1,round(191.69+0.18,2)),
    (0.7,50000,20,'',20,20,'rural','los',1.5,1,42,1,round(164.21+0.18,2)),
    ])


def test_extended_hata(frequency, distance, ant_height, ant_type,
    building_height, street_width, settlement_type, type_of_sight,
    ue_height, above_roof, seed_value, iterations, expected):

    assert (
        extended_hata(frequency, distance, ant_height, ant_type, \
        building_height, street_width, settlement_type, type_of_sight, \
        ue_height, above_roof, seed_value, iterations)
        ) == expected


#Test errors for Extended HATA
def test_extended_hata_model_value_errors():

    with pytest.raises(ValueError):
        extended_hata(0.7,100000,20,'',20,20,'rural','los',1.5,1,1,42)

    with pytest.raises(ValueError, match='Distance over 100km not compliant'):
        extended_hata(4,2000000,20,'macro',20,20,'urban','los',1.5,1,42,1)

    with pytest.raises(
        ValueError, match='Carrier frequency incorrect for Extended Hata'):
        extended_hata(7,200,20,'macro',20,20,'urban','los',1.5,1,42,1)

    with pytest.raises(
        ValueError, match='Could not determine if cell is above or below roof line'):
        extended_hata(1,50,15,'macro',20,20,'urban','los',1.5,'unknown',42,1)

    with pytest.raises(
        ValueError, match='Could not determine if cell is above or below roof line'):
        extended_hata(1,150,15,'macro',20,20,'urban','los',1.5,'unknown',42,1)

    with pytest.raises(
        ValueError, match='Could not determine if cell is above or below roof line'):
        extended_hata(1,400,15,'macro',20,20,'urban','los',1.5,'unknown',42,1)


#prepare for testing UMa NLOS optional model
@pytest.mark.parametrize("frequency, distance, ant_height, ue_height, \
    seed_value, iterations, expected", [
    #expected value is: (deterministic path loss, stochastic component)
    (3.5,1000.41,30,1.5,42,1,round((133.29+3.26),2)),
    (3.5,5000.08,30,1.5,42,1, round((154.25+3.26),2)),
    (3.5,10000.04,30,1.5,42,1, round((163.28+3.26),2)),
    (3.5,20000.02,30,1.5,42,1, round((172.31+3.26),2)),
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
    (1.8,500,20,'',20,20,'urban','nlos',1.5,0,False,42,1,(round(129.12+0.16,2), 'extended_hata_path_loss')),
    (1.8,500,20,'',20,20,'urban','nlos',1.5,0,True,42,1,(round(129.12+0.16+2.05,2), 'extended_hata_path_loss')),
    (3.5,500,35,'macro',10,20,'suburban','nlos',1.5,0,False,42,1,(round(124.28+3.26,2), 'uma_nlos_optional')),
    (3.5,500,35,'macro',10,20,'suburban','nlos',1.5,0,True,42,1,(round(124.28+3.26+5.05,2), 'uma_nlos_optional')),
])


def test_path_loss_calculator(frequency, distance, ant_height, ant_type,
    building_height,street_width, settlement_type, type_of_sight, ue_height,
    above_roof, indoor, seed_value, iterations, expected):

    assert (
        path_loss_calculator(frequency, distance, ant_height, ant_type,
        building_height, street_width, settlement_type, type_of_sight,
        ue_height, above_roof, indoor, seed_value, iterations)
        ) == expected


#Prepare for testing determine_path_loss
@pytest.mark.parametrize("free_space_path_loss, extended_hata_path_loss, \
    expected", [
    (200, 100, (200, 'free_space_path_loss')),
    (100, 200, (200, 'extended_hata_path_loss')),
    ])


def test_determine_path_loss(free_space_path_loss,extended_hata_path_loss,
    expected):

    assert (
        determine_path_loss(free_space_path_loss, extended_hata_path_loss)
        ) == expected
