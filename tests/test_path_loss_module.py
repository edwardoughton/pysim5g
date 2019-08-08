import pytest
from digital_comms.mobile_network.path_loss_module import (
    path_loss_calculator,
    determine_path_loss,
    free_space,
    extended_hata,
    # e_utra_3gpp_tr36_814,
    uma_nlos_optional,
    # check_applicability
    )

#prepare for testing Free Space model
@pytest.mark.parametrize("frequency, distance, ant_height, ue_height, \
    seed_value, iterations, expected", [
    #seed=42
    #expected value is: (deterministic path loss, stochastic component)
    (0.8,1000,20,1.5,42,1,(90.46+1.03)),
    (0.8,2000,20,1.5,42,1,(96.48+1.03)),
    (0.8,3000,20,1.5,42,1,(100+1.03)),
    (0.8,4000,20,1.5,42,1,(102.5+1.03)),
    (0.8,5000,20,1.5,42,1,(104.44+1.03)),
    (1.8,1000,20,1.5,42,1,(97.51+1.03)),
    (1.8,2000,20,1.5,42,1,(103.53+1.03)),
    (1.8,3000,20,1.5,42,1,(107.05+1.03)),
    (1.8,4000,20,1.5,42,1,(109.55+1.03)),
    (1.8,5000,20,1.5,42,1,(111.48+1.03)),
    (2.6,1000,20,1.5,42,1,(100.7+1.03)),
    (2.6,2000,20,1.5,42,1,(106.72+1.03)),
    (2.6,3000,20,1.5,42,1,(110.24+1.03)),
    (2.6,4000,20,1.5,42,1,(112.74+1.03)),
    (2.6,5000,20,1.5,42,1,(round(114.68+1.03,2))),
    ])

def test_free_space(frequency, distance, ant_height, ue_height, seed_value,
    iterations, expected):
    assert (
        free_space(frequency, distance, ant_height, ue_height, seed_value,
        iterations)
        ) == expected


#prepare for testing UMa NLOS optional model
@pytest.mark.parametrize("frequency, distance, ant_height, ue_height, \
    seed_value, iterations, expected", [
    #seed=42
    #expected value is: (deterministic path loss, stochastic component)
    (3.5,1000.41,30,1.5,42,1,round((133.29+0.79),2)),
    (3.5,5000.08,30,1.5,42,1, round((154.25+0.79),2)),
    (3.5,10000.04,30,1.5,42,1, round((163.28+0.79),2)),
    (3.5,20000.02,30,1.5,42,1, round((172.31+0.79),2)),
    ])

def test_uma_nlos_optional(frequency, distance, ant_height, ue_height, seed_value,
    iterations, expected):
    assert (
        uma_nlos_optional(frequency, distance, ant_height, ue_height, seed_value,
        iterations)) == expected


### prepare for testing Extended HATA model
@pytest.mark.parametrize("frequency, distance, ant_height, ant_type, \
    building_height, street_width, settlement_type, type_of_sight, \
    ue_height, above_roof, seed_value, iterations, expected", [
    ###urban####
    # test distance <0.04 km
    (0.8,20,20,'macro',20,20,'urban','los',1.5,1,42,1,(59.17+0.97)),
    # test distance <0.04 km, above roof
    (0.1,200,20,'macro',20,20,'urban','los',1.5,1,42,1,round(81.65+0.7,2)),
    # test distance >0.04 km, below roof
    (0.1,200,20,'',20,20,'urban','nlos',1.5,0,42,1,(81.65+0.64)),
    # test distance >0.04 km, above roof
    (0.8,200,20,'',20,20,'urban','los',1.5,1,42,1,(104.14+0.7)),
    # test distance >0.04 km, below roof
    (0.8,200,20,'',20,20,'urban','nlos',1.5,0,42,1,(104.14+0.64)),
    # test distance >0.04 km, above roof
    (1.8,200,20,'',20,20,'urban','los',1.5,1,42,1,(115.10+0.7)),
    # test distance >0.04 km, below roof
    (1.8,200,20,'',20,20,'urban','nlos',1.5,0,42,1,(round(115.10+0.64,2))),
    # test distance >0.04 km, above roof
    (2.1,200,20,'',20,20,'urban','los',1.5,1,42,1,(116.85+0.7)),
    # test distance >0.04 km, below roof
    (2.1,200,20,'',20,20,'urban','nlos',1.5,0,42,1,(round(116.85+0.64,2))),
    ####suburban####
    # test distance >0.04 km, above roof
    (0.8,200,20,'',20,20,'suburban','los',1.5,1,42,1,(94.50+0.7)),
    # test distance >0.04 km, below roof
    (0.8,200,20,'',20,20,'suburban','nlos',1.5,0,42,1,(94.50+0.64)),
    # test distance 0.5 km, above roof
    (0.8,500,20,'',20,20,'suburban','los',1.5,1,42,1,(round(108.51+0.75,2))),
    # test distance 0.5 km, above roof
    (0.8,500,20,'',20,20,'suburban','los',1.5,0,42,1,(round(108.51+0.81,2))),
    ####rural####
    # test distance >0.04 km, above roof
    (1.8,200,20,'',20,20,'rural','los',1.5,1,42,1,(83.17+0.7)),
    #####test 500m####
    # test distance 0.05 km, above roof
    (1.8,500,20,'',20,20,'urban','los',1.5,1,42,1,(round(129.12+0.75,2))),
    # test distance 0.05 km, below roof
    (1.8,500,20,'',20,20,'urban','nlos',1.5,0,42,1,(129.12+0.81)),
    #change distances
    #test 90m (0.04< d <0.1)
    # test distance 0.09 km, above roof
    (1.8,90,20,'',20,20,'urban','los',1.5,1,42,1,(round(76.82+0.8,2))),
    # test distance 0.09 km, below roof
    (1.8,90,20,'',20,20,'urban','nlos',1.5,0,42,1,(round(76.82+0.74,2))),
    #test 5km
    # test distance 5 km, above roof
    (1.8,5000,20,'',20,20,'urban','los',1.5,1,42,1,(164.34+0.7)),
    # test distance 5 km, above roof
    (1.8,5000,20,'',20,20,'rural','los',1.5,1,42,1,(round(132.42+0.7,2))),
    #test 20km
    # test distance 20 km, above roof
    (0.7,20000,20,'',20,20,'urban','los',1.5,1,42,1,(round(173.07+0.7,2))),
    (0.7,20000,20,'',20,20,'rural','los',1.5,1,42,1,(round(145.59+0.7,2))),
    #test 21km
    # test distance 21 km, above roof
    (0.7,21000,20,'',20,20,'urban','los',1.5,1,42,1,(173.99+0.7)),
    (0.7,21000,20,'',20,20,'rural','los',1.5,1,42,1,(round(146.51+0.7,2))),
    # test distance 25 km, above roof
    (0.7,25000,20,'',20,20,'urban','los',1.5,1,42,1,(177.24+0.7)),
    (0.7,25000,20,'',20,20,'rural','los',1.5,1,42,1,(round(149.76+0.7,2))),
    #test 50km
    # test distance 50 km, above roof
    (0.7,50000,20,'',20,20,'urban','los',1.5,1,42,1,(191.69+0.7)),
    (0.7,50000,20,'',20,20,'rural','los',1.5,1,42,1,(164.21+0.7)),
    ])


def test_extended_hata(frequency, distance, ant_height, ant_type,
    building_height, street_width, settlement_type, type_of_sight,
    ue_height, above_roof, seed_value, iterations, expected):
    assert (
        extended_hata(frequency, distance, ant_height, ant_type, \
        building_height, street_width, settlement_type, type_of_sight, \
        ue_height, above_roof, seed_value, iterations)
        ) == expected

    with pytest.raises(ValueError):
        extended_hata(0.7,100000,20,'',20,20,'rural','los',1.5,1,1,42)


#Test errors for Extended HATA
def test_extended_hata_model_value_errors():

    msg = 'Distance over 100km not compliant'

    with pytest.raises(ValueError) as ex1:
        extended_hata(4,2000000,20,'macro',20,20,'urban','los',1.5,1,42,1)

    assert msg in str(ex1)

    msg = 'Carrier frequency incorrect for Extended Hata'

    with pytest.raises(ValueError) as ex1:
        extended_hata(7,200,20,'macro',20,20,'urban','los',1.5,1,42,1)

    assert msg in str(ex1)

    #'unknown' used to test if cell neither above or below roof line
    msg = 'Could not determine if cell is above or below roof line'

    with pytest.raises(ValueError) as ex1:
        extended_hata(1,50,15,'macro',20,20,'urban','los',1.5,'unknown',42,1)

    assert msg in str(ex1)

    with pytest.raises(ValueError) as ex2:
        extended_hata(1,150,15,'macro',20,20,'urban','los',1.5,'unknown',42,1)

    assert msg in str(ex2)

    with pytest.raises(ValueError) as ex3:
        extended_hata(1,400,15,'macro',20,20,'urban','los',1.5,'unknown',42,1)

    assert msg in str(ex3)


# #Prepare for testing 3GPP E-UTRA
# @pytest.mark.parametrize("frequency, distance, ant_height, ant_type, \
#     building_height, street_width, settlement_type, type_of_sight, \
#     ue_height, seed_value, expected", [
#     #stochastic component is 0.68 (seed=42)
#     (3.5,500,10,'micro',20,20,'urban','los',1.5,42, (round(98.26+1,2))),
#     (3.5,1000,10,'micro',20,20,'urban','los',1.5,42, (round(107.72+1,2))),
#     (3.5,6000,10,'micro',20,20,'urban','los',1.5,42, 136.68),
#     # #stochastic component is 0.56 (seed=42)
#     (3.5,500,10,'micro',20,20,'urban','nlos',1.5,42, (135.90+0.94)),
#     (3.5,500,25, 'macro',20,20,'urban','los',1.5,42, (round(98.26+0.94,2))),
#     (3.5,2000,25,'macro',20,20,'urban','los',1.5,42, round(112.6+0.94,2)),
#     (3.5,6000,10,'macro',20,20,'urban','los',1.5,42, 136.62),
#     #stochastic component is 0.42 (seed=42)
#     (3.5,1000,25,'macro',20,20,'urban','nlos',1.5,42, (round(141.69+0.85,2))),
#     (3.5,6000,10,'macro',20,20,'urban','nlos',1.5,42, 191.91),
#     #stochastic component is 0.56 (seed=42)
#     (3.5,1000,35,'macro',10,20,'suburban','los',1.5,42, round(107.74+0.94,2)),
#     #stochastic component is 0.56 & 0.42 (seed=42)
#     (3.5,4000,35,'macro',10,20,'suburban','los',1.5,42, (round(126.73+0.94+0.85,2))),
#     #stochastic component is 0.34 (seed=42)
#     (3.5,500,35,'macro',10,20,'suburban','nlos',1.5,42, (121.39+0.79)),
#     (3.5,6000,10,'macro',80,20,'suburban','los',1.5,42, 164.12),
#     #stochastic component is 0.56 (seed=42)
#     (3.5,1000,35,'macro',10,20,'rural','los',1.5,42, round(107.74+0.94,2)),
#     #stochastic component is 0.56 + 0.42 (seed=42)
#     (3.5,4000,35,'macro',10,20,'rural','los',1.5,42, (round(126.73+0.85+0.94,2))),
#     #stochastic component is 0.34 (seed=42)
#     (3.5,500,35,'macro',10,20,'rural','nlos',1.5,42, (121.39+0.79)),
#     (3.5,6000,10,'macro',80,20,'rural','nlos',1.5,42, 418.36),
#     ])


# def test_eval_path_loss_calc(frequency, distance, ant_height, ant_type,
#     building_height, street_width, settlement_type, type_of_sight,
#     ue_height, seed_value, expected):

#     assert (
#         e_utra_3gpp_tr36_814(frequency, distance, ant_height, ant_type, \
#         building_height, street_width, settlement_type, type_of_sight, \
#         ue_height, seed_value)
#         ) == expected

#     with pytest.raises(ValueError):
#         e_utra_3gpp_tr36_814(3.5,1000,35,'macro',10,80,'rural','los',1.5,
#         42)

#     with pytest.raises(ValueError):
#         e_utra_3gpp_tr36_814(3.5,1000,35,'macro',10,80,'rural','los',11.5,
#         42)


# #Prepare for testing 3GPP compatability function
# @pytest.mark.parametrize("building_height, street_width, ant_height, \
#     ue_height, expected", [
#     (20, 20, 20, 1.5, True),
#     (5, 20, 8, 1.5, False), ])

# def test_check_applicability(building_height, street_width, ant_height,
#     ue_height, expected):
#     assert (
#         check_applicability(building_height, street_width, ant_height,
#         ue_height)
#         ) == expected


# def test_path_loss_calculator_errors():

#     with pytest.raises(ValueError) as ex:
#         path_loss_calculator(
#             0.01,500,10,'micro',20,20,'urban','los',1.5,1, True, 42
#             )

#     msg = 'frequency of 0.01 is NOT within correct range'

#     assert msg in str(ex)


# #Prepare for testing path_loss_calculator
# @pytest.mark.parametrize("frequency, distance, ant_height, ant_type, \
#     building_height, street_width, settlement_type, type_of_sight, \
#     ue_height, above_roof, indoor, seed_value, expected", [
#     (1.8,500,20,'',20,20,'urban','nlos',1.5,0,False,42, round(129.12+0.81,2)),
#     (3.5,500,35,'macro',10,20,'suburban','nlos',1.5,0,False,42, (121.39+0.79)),
#     (1.8,500,40,'',20,20,'urban','nlos',1.5,0,True,42, round(124.11+0.81+3.31,2)),
#     (3.5,500,40,'macro',10,20,'suburban','nlos',1.5,0,True,42,(119.94+0.79+3.31)),
# ])


# def test_path_loss_calculator(frequency, distance, ant_height, ant_type,
#     building_height,street_width, settlement_type, type_of_sight, ue_height,
#     above_roof, indoor, seed_value, expected):

#     assert (
#         path_loss_calculator(frequency, distance, ant_height, ant_type,
#         building_height, street_width, settlement_type, type_of_sight,
#         ue_height, above_roof, indoor, seed_value)
#         ) == expected


# #Prepare for testing determine_path_loss
# @pytest.mark.parametrize("extended_hata_path_loss, free_space_path_loss, \
#     expected", [
#     (100, 200, 200),
#     (200, 100, 200),
#     ])


# def test_determine_path_loss(extended_hata_path_loss, free_space_path_loss,
#     expected):
#     assert (
#         determine_path_loss(extended_hata_path_loss, free_space_path_loss)
#         ) == expected
