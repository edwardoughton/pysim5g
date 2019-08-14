"""
Path Loss Calculator

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
        Indicates the type of cell (hotspot, micro, macro).
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
    if 0.03 < frequency <= 3:

        free_space_path_loss = free_space(
            frequency, distance, ant_height, ue_height, seed_value, iterations
        )

        extended_hata_path_loss = extended_hata(
            frequency, distance, ant_height, ant_type, building_height,
            street_width, settlement_type, type_of_sight, ue_height,
            above_roof, seed_value, iterations
        )

        path_loss, model = determine_path_loss(
            free_space_path_loss, extended_hata_path_loss
        )

    elif 3 <= frequency < 6:

        path_loss = uma_nlos_optional(frequency, distance, ant_height,
            ue_height, seed_value, iterations)

        model = 'uma_nlos_optional'

    else:

        raise ValueError (
            "frequency of {} is NOT within correct range".format(frequency)
        )

    path_loss = path_loss + outdoor_to_indoor_path_loss(
        frequency, indoor, seed_value
    )

    return round(path_loss, 2), model


def determine_path_loss(free_space_path_loss, extended_hata_path_loss):
    """

    Model guidance states that 'when L [median path loss] is below
    the free space attenuation for the same distance, the free space
    attenuation is used instead.'

    Parameters
    ----------
    free_space_path_loss : int
        The path loss resulting from the use of the Free Space model (dB).
    extended_hata_path_loss : int
        The path loss resulting from the use of the Extended Hata model (dB).

    Returns
    -------
    path_loss : float
        Path loss in decibels (dB)
    model : string
        Type of model used for path loss estimation.

    """
    if extended_hata_path_loss < free_space_path_loss:

        path_loss = free_space_path_loss

        model = 'free_space_path_loss'
    else:

        path_loss = extended_hata_path_loss

        model = 'extended_hata_path_loss'

    return path_loss, model


def free_space(frequency, distance, ant_height, ue_height,
    seed_value, iterations):
    """
    Implements the Free Space path loss model.

    Parameters
    ----------
    frequency : int
        Carrier band (f) required in MHz.
    distance : int
        Distance (d) between transmitter and receiver (km).
    ant_height : int
        Transmitter antenna height (h1) (m, above ground).
    ue_height : int
        Receiver antenna height (h2) (m, above ground).
    sigma : int
        Variation in path loss (dB) which is 2.5dB for free space.

    Returns
    -------
    path_loss : float
        Path loss in decibels (dB)

    """
    #model requires frequency in MHz rather than GHz.
    frequency = frequency*1000
    #model requires distance in kilometers rather than meters.
    distance = distance/1000

    random_variation = generate_log_normal_dist_value(
        frequency, 1, 2.5, iterations, seed_value
    )

    path_loss = (
        32.4 + 10*np.log10((((ant_height - ue_height)/1000)**2 + \
        distance**2)) + (20*np.log10(frequency) + random_variation)
    )

    return round(path_loss, 2)


def extended_hata(frequency, distance, ant_height, ant_type, building_height,
    street_width, settlement_type, type_of_sight, ue_height, above_roof,
    seed_value, iterations):
    """
    Implements the Extended Hata path loss model.

    Parameters
    ----------
    frequency : int
        Carrier band (f) required in MHz.
    distance : int
        Distance (d) between transmitter and receiver (km).
    ant_height : int
        Transmitter antenna height (h1) (m, above ground).
    ue_height : int
        Receiver antenna height (h2) (m, above ground).
    env : string
        General environment (urban/suburban/rural)
    L : int
        Median path loss (dB)
    sigma : int
        Variation in path loss (dB)

    Returns
    -------
    path_loss : float
        Path loss in decibels (dB)

    """
    #model requires frequency in MHz rather than GHz.
    frequency = frequency*1000
    #model requires distance in kilometers rather than meters.
    distance = distance/1000

    #find smallest value
    hm = min(ant_height, ue_height)
    #find largest value
    hb = max(ant_height, ue_height)

    alpha_hm = (1.1*np.log10(frequency) - 0.7) * min(10, hm) - \
        (1.56*np.log10(frequency) - 0.8) + max(0, (20*np.log10(hm/10)))

    beta_hb = min(0, (20*np.log10(hb/30)))

    if distance <= 20: #units : km

        alpha_exponent = 1

    elif 20 < distance < 100: #units : km

        alpha_exponent = 1 + (0.14 + 1.87e-4 * frequency + \
            1.07e-3 * hb)*(np.log10(distance/20))**0.8

    else:
        raise ValueError('Distance over 100km not compliant')

    ###PART 1####
    #Determine initial path loss according to distance, frequency
    # and environment.
    if distance < 0.04:

        path_loss = (
            32.4 + (20*np.log10(frequency)) + (10*np.log10((distance**2) +
            ((hb - hm)**2) / (10**6)))
        )

    elif distance >= 0.1:

        if 30 < frequency <= 150:

            path_loss = (
                69.6 + 26.2*np.log10(150) - 20*np.log10(150/frequency) -
                13.82*np.log10(max(30, hb)) +
                (44.9 - 6.55*np.log10(max(30, hb))) *
                np.log10(distance)**alpha_exponent - alpha_hm - beta_hb
            )

        elif 150 < frequency <= 1500:

            path_loss = (
                69.6 + 26.2*np.log10(frequency) -
                13.82*np.log10(max(30, hb)) +
                (44.9 - 6.55*np.log10(max(30, hb))) *
                ((np.log10(distance))**alpha_exponent) - alpha_hm - beta_hb
            )

        elif 1500 < frequency <= 2000:

            path_loss = (
                46.3 + 33.9*np.log10(frequency) -
                13.82*np.log10(max(30, hb)) +
                (44.9 - 6.55*np.log10(max(30, hb))) *
                (np.log10(distance))**alpha_exponent - alpha_hm - beta_hb
            )

        elif 2000 < frequency <= 4000:

            path_loss = (
                46.3 + 33.9*np.log10(2000) +
                10*np.log10(frequency/2000) -
                13.82*np.log10(max(30, hb)) +
                (44.9 - 6.55*np.log10(max(30, hb))) *
                (np.log10(distance))**alpha_exponent - alpha_hm - beta_hb
            )

        else:
            raise ValueError('Carrier frequency incorrect for Extended Hata')

        if settlement_type == 'suburban':

            path_loss = (
                path_loss - 2 * \
                (np.log10((min(max(150, frequency), 2000)/28)))**2 - 5.4
            )

        elif settlement_type == 'rural': #also called 'open area'

            path_loss = (
                path_loss - 4.78 * \
                (np.log10(min(max(150, frequency), 2000)))**2 + 18.33 * \
                    np.log10(min(max(150, frequency), 2000)) - 40.94
            )

        else:
            pass

    elif 0.04 <= distance < 0.1:

        #distance pre-set at 0.1
        l_fixed_distance_upper = (
            32.4 + (20*np.log10(frequency)) + (10*np.log10(0.1**2 +
            (hb - hm)**2 / 10**6))
        )

        #distance pre-set at 0.04
        l_fixed_distance_lower = (
            32.4 + (20*np.log10(frequency)) + (10*np.log10(0.04**2 +
            (hb - hm)**2 / 10**6))
        )

        path_loss = (l_fixed_distance_lower +
            (np.log10(distance) - np.log10(0.04)) / \
            (np.log10(0.1) - np.log10(0.04)) *
            (l_fixed_distance_upper - l_fixed_distance_lower)
        )

    else:

        raise ValueError('Distance over 100km not compliant')

    ###PART 2####
    #determine variation in path loss using stochastic component
    if distance <= 0.04:

        path_loss = path_loss + generate_log_normal_dist_value(
            frequency, 1, 3.5, iterations, seed_value
        )

    elif 0.04 < distance <= 0.1:

        if above_roof == 1:

            sigma = (3.5 + ((12-3.5)/0.1-0.04) * (distance - 0.04))
            random_quantity = generate_log_normal_dist_value(
                frequency, 1, sigma, iterations, seed_value
            )

            path_loss = (
                path_loss + random_quantity
            )

        elif above_roof == 0:

            sigma = (3.5 + ((17-3.5)/0.1-0.04) * (distance - 0.04))
            random_quantity = generate_log_normal_dist_value(
                frequency, 1, sigma, iterations, seed_value
            )

            path_loss = (
                path_loss + random_quantity
            )

        else:
            raise ValueError(
                'Could not determine if cell is above or below roof line'
            )

    elif 0.1 < distance <= 0.2:

        if above_roof == 1:

            random_quantity = generate_log_normal_dist_value(
                frequency, 1, 12, iterations, seed_value
            )

            path_loss = (
                path_loss + random_quantity
            )

        elif above_roof == 0:

            random_quantity = generate_log_normal_dist_value(
                frequency, 1, 17, iterations, seed_value
            )

            path_loss = (
                path_loss + random_quantity
            )

        else:
            raise ValueError(
                'Could not determine if cell is above or below roof line'
            )

    elif 0.2 < distance <= 0.6:

        if above_roof == 1:

            sigma = (12 + ((9-12)/0.6-0.2) * (distance - 0.02))

            random_quantity = generate_log_normal_dist_value(
                frequency, 1, sigma, iterations, seed_value
            )

            path_loss = (
                path_loss + random_quantity
            )

        elif above_roof == 0:

            sigma = (17 + (9-17) / (0.6-0.2) * (distance - 0.02))

            random_quantity = generate_log_normal_dist_value(
                frequency, 1, sigma, iterations, seed_value
            )

            path_loss = (
                path_loss + random_quantity
            )

        else:
            raise ValueError(
                'Could not determine if cell is above or below roof line'
            )

    elif 0.6 < distance:

        random_quantity = generate_log_normal_dist_value(
            frequency, 1, 12, iterations, seed_value
        )

        path_loss = (
            path_loss + random_quantity
        )

    return round(path_loss, 2)


def uma_nlos_optional(frequency, distance, ant_height, ue_height,
    seed_value, iterations):
    """

    UMa NLOS / Optional from ETSI TR 138.901 / 3GPP TR 38.901

    Parameters
    ----------
    frequency : int
        Carrier band (f) required in MHz.
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
    distance_3d = sqrt((distance)**2 + (ant_height - ue_height)**2)

    path_loss = 32.4 + 20*np.log10(frequency) + 30*np.log10(distance_3d)

    random_variation = generate_log_normal_dist_value(
        frequency, 1, 7.8, iterations, seed_value
    )

    return round(path_loss + random_variation, 2)


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
