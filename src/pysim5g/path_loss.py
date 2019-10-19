"""
Path loss calculator

Author: Edward Oughton
Date: April 2019

An implementation of a path loss calculator utilising (i) a Free Space model,
(ii) the Extended Hata model (150 MHz - 3 GHz) as found in the following
documents:

ITU-R SM.2028-2
Monte Carlo simulation methodology for the use in sharing and compatibility
studies between different radio services or systems.

"""
import numpy as np
from math import pi, sqrt


def path_loss_calculator(frequency, distance, ant_height, ant_type,
    building_height, street_width, settlement_type, type_of_sight,
    ue_height, above_roof, indoor, seed_value, iterations):
    """
    Calculate the correct path loss given a range of critera.

    Parameters
    ----------
    frequency : float
        Frequency band given in GHz.
    distance : float
        Distance between the transmitter and receiver in km.
    ant_height:
        Height of the antenna.
    ant_type : string
        Indicates the type of site antenna (hotspot, micro, macro).
    building_height : int
        Height of surrounding buildings in meters (m).
    street_width : float
        Width of street in meters (m).
    settlement_type : string
        Gives the type of settlement (urban, suburban or rural).
    type_of_sight : string
        Indicates whether the path is (Non) Line of Sight (LOS or NLOS).
    ue_height : float
        Height of the User Equipment.
    above_roof : int
        Indicates if the propagation line is above or below building roofs.
        Above = 1, below = 0.
    indoor : binary
        Indicates if the user is indoor (True) or outdoor (False).
    seed_value : int
        Dictates repeatable random number generation.
    iterations : int
        Specifies how many iterations a specific calculation should be run for.

    Returns
    -------
    path_loss : float
        Path loss in decibels (dB)
    model : string
        Type of model used for path loss estimation.

    """
    if 0.05 < frequency <= 100:

        path_loss = etsi_tr_138_901(frequency, distance, ant_height, ant_type,
            building_height, street_width, settlement_type, type_of_sight,
            ue_height, above_roof, indoor, seed_value, iterations
        )

        path_loss = path_loss + outdoor_to_indoor_path_loss(
            frequency, indoor, seed_value
        )

        model = 'etsi_tr_138_901'

    else:

        raise ValueError (
            "frequency of {} is NOT within correct range".format(frequency)
        )

    return round(path_loss), model


def etsi_tr_138_901(frequency, distance, ant_height, ant_type,
    building_height, street_width, settlement_type, type_of_sight,
    ue_height, above_roof, indoor, seed_value, iterations):
    """

    Model requires:
        - Frequency in gigahertz
        - Distance in meters

    c = speed of light
    he = effective environment height
    hbs = effective antenna height
    hut = effective user terminal height

    """
    fc = frequency
    c = 3e8

    he = 1 #enviroment_height
    hbs = ant_height
    hut = ue_height
    h_apost_bs = ant_height - ue_height
    h_apost_ut = ue_height - he
    w = street_width # mean street width is 20m
    h = building_height # mean building height

    dbp = 2 * pi * hbs * hut * (fc * 1e9) / c
    d_apost_bp = 4 * h_apost_bs * h_apost_ut * (fc*1e9) / c
    d2d_in = 10 #mean d2d_in value
    d2d_out = distance - d2d_in
    d2d = d2d_out + d2d_in
    d3d = sqrt((d2d_out + d2d_in)**2 + (hbs - hut)**2)

    check_3gpp_applicability(building_height, street_width, ant_height, ue_height)

    if ant_type == 'macro':
        if settlement_type == 'suburban' or settlement_type == 'rural':
            pl1 = round(
                20*np.log10(40*pi*d3d*fc/3) + min(0.03*h**1.72,10) *
                np.log10(d3d) - min(0.044*h**1.72,14.77) +
                0.002*np.log10(h)*d3d +
                generate_log_normal_dist_value(fc, 1, 4, iterations, seed_value)
            )

            if 10 <= d2d <= dbp:
                if type_of_sight == 'los':
                    return pl1
            pl_rma_los = pl1

            pl2 = round(
                20*np.log10(40*pi*dbp*fc/3) + min(0.03*h**1.72,10) *
                np.log10(dbp) - min(0.044*h**1.72,14.77) +
                0.002*np.log10(h)*dbp +
                generate_log_normal_dist_value(fc, 1, 4, iterations, seed_value) +
                40*np.log10(d3d / dbp) +
                generate_log_normal_dist_value(fc, 1, 6, iterations, seed_value)
            )

            if dbp <= d2d <= 10000:
                if type_of_sight == 'los':
                    return pl2
            pl_rma_los = pl2

            if type_of_sight == 'nlos':

                pl_apostrophe_rma_nlos = round(
                    161.04 - 7.1 * np.log10(w)+7.5*np.log10(h) -
                    (24.37 - 3.7 * (h/hbs)**2)*np.log10(hbs) +
                    (43.42 - 3.1*np.log10(hbs))*(np.log10(d3d)-3) +
                    20*np.log10(fc) - (3.2 * (np.log10(11.75*hut))**2 - 4.97) +
                    generate_log_normal_dist_value(fc, 1, 8, iterations, seed_value)
                )

                # # currently does not cap at 5km, which this should
                pl_rma_nlos = max(pl_apostrophe_rma_nlos, pl_rma_los)

                return pl_rma_nlos

            if d2d > 10000:
                return uma_nlos_optional(frequency, distance, ant_height, ue_height,
                    seed_value, iterations)

        elif settlement_type == 'urban':

            pl1 = round(
                28 + 22 * np.log10(d3d) + 20 * np.log10(fc) +
                generate_log_normal_dist_value(fc, 1, 4, iterations, seed_value)
            )

            if 10 <= d2d <= d_apost_bp:
                if type_of_sight == 'los':
                    return pl1
                pl_uma_los = pl1

            pl2 = round(
                28 + 40*np.log10(d3d) + 20 * np.log10(fc) -
                9*np.log10((d_apost_bp)**2 + (hbs-hut)**2) +
                generate_log_normal_dist_value(fc, 1, 4, iterations, seed_value)
            )

            if d_apost_bp <= d2d <= 5000:
                if type_of_sight == 'los':
                    return pl2
            pl_uma_los = pl2

            if type_of_sight == 'nlos':

                if d2d <= 5000:
                    pl_apostrophe_uma_nlos = round(
                        13.54 + 39.08 * np.log10(d3d) + 20 *
                        np.log10(fc) - 0.6 * (hut - 1.5) +
                        generate_log_normal_dist_value(fc, 1, 6, iterations, seed_value)
                    )

                if d2d > 5000:
                    pl_apostrophe_uma_nlos = uma_nlos_optional(frequency, distance, ant_height,
                        ue_height, seed_value, iterations)

                pl_uma_nlos = max(pl_apostrophe_uma_nlos, pl_uma_los)

                return pl_uma_nlos

        else:
            # return uma_nlos_optional(frequency, distance, ant_height, ue_height,
            #     seed_value, iterations)
            raise ValueError('Did not recognise settlement_type')

    elif ant_type == 'micro':

            pl1 = round(
                32.4 + 21 * np.log10(d3d) + 20 * np.log10(fc) +
                generate_log_normal_dist_value(fc, 1, 4, iterations, seed_value)
            )

            if 10 <= d2d <= d_apost_bp:
                if type_of_sight == 'los':
                    return pl1
                pl_umi_los = pl1

            pl2 = round(
                32.4 + 40*np.log10(d3d) + 20 * np.log10(fc) -
                9.5*np.log10((d_apost_bp)**2 + (hbs-hut)**2) +
                generate_log_normal_dist_value(fc, 1, 4, iterations, seed_value)
            )

            if d_apost_bp <= d2d <= 5000:
                if type_of_sight == 'los':
                    return pl2
            pl_umi_los = pl2

            if type_of_sight == 'nlos':

                if d2d <= 5000:
                    pl_apostrophe_umi_nlos = round(
                        35.3 * np.log10(d3d) + 22.4 +
                        21.3 * np.log10(fc) - 0.3 * (hut - 1.5) +
                        generate_log_normal_dist_value(fc, 1, 7.82, iterations, seed_value)
                    )

                pl_uma_nlos = max(pl_apostrophe_umi_nlos, pl_umi_los)

                return pl_uma_nlos

    else:
        raise ValueError('Did not recognise ant_type')

    return 'complete'


def uma_nlos_optional(frequency, distance, ant_height, ue_height,
    seed_value, iterations):
    """

    UMa NLOS / Optional from ETSI TR 138.901 / 3GPP TR 38.901

    Parameters
    ----------
    frequency : int
        Carrier band (f) required in GHz.
    distance : int
        Distance (d) between transmitter and receiver (km).
    ant_height : int
        Transmitter antenna height (h1) (m, above ground).
    ue_height : int
        Receiver antenna height (h2) (m, above ground).
    sigma : int
        Variation in path loss (dB) which is 2.5dB for free space.
    seed_value : int
        Dictates repeatable random number generation.
    iterations : int
        Specifies iterations for a specific calculation.

    Returns
    -------
    path_loss : float
        Path loss in decibels (dB)

    """
    fc = frequency
    d3d = sqrt((distance)**2 + (ant_height - ue_height)**2)

    path_loss = 32.4 + 20*np.log10(fc) + 30*np.log10(d3d)

    random_variation = generate_log_normal_dist_value(
        frequency, 1, 7.8, iterations, seed_value
    )

    return round(path_loss + random_variation)


def check_3gpp_applicability(building_height, street_width, ant_height, ue_height):

    if 5 <= building_height < 50 :
        building_height_compliant = True
    else:
        building_height_compliant = False
        print('building_height not compliant')

    if 5 <= street_width < 50:
        street_width_compliant = True
    else:
        street_width_compliant = False
        print('Street_width not compliant')

    if 10 <= ant_height < 150:
        ant_height_compliant = True
    else:
        ant_height_compliant = False
        print('ant_height not compliant')

    if 1 <= ue_height < 10:
        ue_height_compliant = True
    else:
        ue_height_compliant = False
        print('ue_height not compliant')

    if (building_height_compliant + street_width_compliant +
        ant_height_compliant + ue_height_compliant) == 4:
        overall_compliant = True
    else:
        overall_compliant = False

    return overall_compliant


def generate_log_normal_dist_value(frequency, mu, sigma, draws, seed_value):
    """
    Generates random values using a lognormal distribution,
    given a specific mean (mu) and standard deviation (sigma).

    https://stackoverflow.com/questions/51609299/python-np-lognormal-gives-infinite-
    results-for-big-average-and-st-dev

    The parameters mu and sigma in np.random.lognormal are not the mean
    and STD of the lognormal distribution. They are the mean and STD
    of the underlying normal distribution.

    Parameters
    ----------
    mu : int
        Mean of the desired distribution.
    sigma : int
        Standard deviation of the desired distribution.
    draws : int
        Number of required values.

    Returns
    -------
    random_variation : float
        Mean of the random variation over the specified itations.

    """
    if seed_value == None:
        pass
    else:
        frequency_seed_value = seed_value * frequency * 100

        np.random.seed(int(str(frequency_seed_value)[:2]))

    normal_std = np.sqrt(np.log10(1 + (sigma/mu)**2))
    normal_mean = np.log10(mu) - normal_std**2 / 2

    hs = np.random.lognormal(normal_mean, normal_std, draws)

    return round(np.mean(hs),2)


def outdoor_to_indoor_path_loss(frequency, indoor, seed_value):
    """

    ITU-R M.1225 suggests building penetration loss for shadow fading can be modelled
    as a log-normal distribution with a mean and  standard deviation of 12 dB and
    8 dB respectively.

    frequency : int
        Carrier band (f) required in MHz.
    indoor : binary
        Indicates if the user is indoor (True) or outdoor (False).
    seed_value : int
        Dictates repeatable random number generation.

    Returns
    -------
    path_loss : float
        Outdoor to indoor path loss in decibels (dB)

    """
    if indoor:

        outdoor_to_indoor_path_loss = generate_log_normal_dist_value(frequency, 12, 8, 1, seed_value)

    else:

        outdoor_to_indoor_path_loss = 0

    return outdoor_to_indoor_path_loss
