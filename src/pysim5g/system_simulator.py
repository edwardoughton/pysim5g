"""
System-level wireless network simulator

Written by Edward Oughton
May 2019

"""
from rtree import index
from shapely.geometry import shape, Point, LineString
import numpy as np
from geographiclib.geodesic import Geodesic
from itertools import tee
from pyproj import Proj, transform
from collections import OrderedDict

from digital_comms.mobile_network.path_loss_module import path_loss_calculator

#set numpy seed
np.random.seed(42)

class SimulationManager(object):
    """
    Meta-object for managing all transmitters and receivers in wireless system.

    Parameters
    ----------
    area : geojson
        Polygon of the simulation area boundary
    sites : list of dicts
        Contains a dict for each cellular transmitter site in a list format.
    receivers : list of dicts
        Contains a dict for each user equipment receiver in a list format.
    simulation_parameters : dict
        A dict containing all simulation parameters necessary.

    """
    def __init__(self, transmitter, interfering_transmitters,
        receivers, cell_area, simulation_parameters):

        self.transmitter = Transmitter(transmitter[0], simulation_parameters)
        self.cell_area = CellArea(cell_area[0])
        self.receivers = {}
        self.interfering_transmitters = {}

        for receiver in receivers:
            receiver_id = receiver['properties']["ue_id"]
            receiver = Receiver(receiver, simulation_parameters)
            self.receivers[receiver_id] = receiver

        for interfering_transmitter in interfering_transmitters:
            site_id = interfering_transmitter['properties']["site_id"]
            site_object = InterferingTransmitter(
                interfering_transmitter, simulation_parameters
                )
            self.interfering_transmitters[site_id] = site_object


    def estimate_link_budget(self, frequency, bandwidth,
        generation, mast_height, environment, modulation_and_coding_lut,
        simulation_parameters):
        """
        Takes propagation parameters and calculates link budget capacity.

        Parameters
        ----------
        frequency : float
            The carrier frequency for the chosen spectrum band (GHz).
        bandwidth : float
            The width of the spectrum around the carrier frequency (MHz).
        environment : string
            Either urban, suburban or rural.
        modulation_and_coding_lut : list of tuples
            A lookup table containing modulation and coding rates,
            spectral efficiencies and SINR estimates.

        Returns
        -------
        sinr : float
            The signal to noise plut interference ratio (GHz).
        capacity_mbps : float
            The estimated link budget capacity.

        """
        results = []

        seed_value1 = simulation_parameters['seed_value1']
        seed_value2 = simulation_parameters['seed_value2']
        iterations = simulation_parameters['iterations']

        for receiver in self.receivers.values():

            path_loss, r_model, r_distance, type_of_sight = self.calculate_path_loss(
                receiver, frequency, environment, seed_value1, iterations
            )

            received_power = self.calc_received_power(self.transmitter,
                receiver, path_loss
            )

            interference, i_model, ave_distance, ave_inf_pl = self.calculate_interference(
                receiver, frequency, environment, seed_value2, iterations)

            noise = self.calculate_noise(
                bandwidth
            )

            f_received_power, f_interference, f_noise, i_plus_n, sinr = \
                self.calculate_sinr(received_power, interference, noise,
                simulation_parameters
                )

            spectral_efficiency = self.modulation_scheme_and_coding_rate(
                sinr, generation, modulation_and_coding_lut
            )

            link_budget_capacity_mbps_km2 = self.link_budget_capacity(
                bandwidth, spectral_efficiency
            )

            results.append({
                'path_loss': path_loss,
                'r_model': r_model,
                'type_of_sight': type_of_sight,
                'ave_inf_pl': ave_inf_pl,
                'received_power': f_received_power,
                'distance': r_distance,
                'interference': np.log10(f_interference),
                'i_model': i_model,
                'network_load': simulation_parameters['network_load'],
                'ave_distance': ave_distance,
                'noise': f_noise,
                'i_plus_n': np.log10(i_plus_n),
                'sinr': sinr,
                'spectral_efficiency': spectral_efficiency,
                'estimated_capacity': link_budget_capacity_mbps_km2,
                'receiver_x': receiver.coordinates[0],
                'receiver_y': receiver.coordinates[1],
                })

            # print('received_power is {}'.format(received_power))
            # print('interference is {}'.format(interference))
            # print('noise is {}'.format(noise))
            # print('sinr is {}'.format(sinr))
            # print('spectral_efficiency is {}'.format(spectral_efficiency))
            # print('estimated_capacity is {}'.format(estimated_capacity))
            # print('path_loss is {}'.format(path_loss))
            # print('-----------------------------')

        return results


    def calculate_path_loss(self, receiver,
        frequency, environment, seed_value, iterations):

        temp_line = LineString([
            (receiver.coordinates[0],
            receiver.coordinates[1]),
            (self.transmitter.coordinates[0],
            self.transmitter.coordinates[1])]
            )

        strt_distance = temp_line.length

        ant_height = self.transmitter.ant_height
        ant_type =  'macro'

        los_distance = 250

        if strt_distance < los_distance :
            type_of_sight = 'los'
        else:
            type_of_sight = 'nlos'

        building_height = 20
        street_width = 20
        above_roof = 0
        location = receiver.indoor

        path_loss, model = path_loss_calculator(
            frequency,
            strt_distance,
            ant_height,
            ant_type,
            building_height,
            street_width,
            environment,
            type_of_sight,
            receiver.ue_height,
            above_roof,
            location,
            seed_value,
            iterations
            )

        return path_loss, model, strt_distance, type_of_sight


    def calc_received_power(self, transmitter, receiver, path_loss):
        """
        Calculate received power based on site and receiver
        characteristcs, and path loss.

        Equivalent Isotropically Radiated Power (EIRP) = Power + Gain - Losses

        """
        #calculate Equivalent Isotropically Radiated Power (EIRP)
        eirp = float(self.transmitter.power) + \
            float(self.transmitter.gain) - \
            float(self.transmitter.losses)

        received_power = eirp - \
            path_loss - \
            receiver.misc_losses + \
            receiver.gain - \
            receiver.losses

        return received_power


    def calculate_interference(
        self, receiver, frequency, environment, seed_value, iterations):
        """
        Calculate interference from other cells.

        closest_sites contains all sites, ranked based
        on distance, meaning we need to select cells 1-3 (as cell 0
        is the actual cell in use)

        """
        interference = []

        x1_receiver, y1_receiver = transform_coordinates(
            Proj(init='epsg:27700'),
            Proj(init='epsg:4326'),
            receiver.coordinates[0],
            receiver.coordinates[1]
            )

        ave_distance = 0
        ave_pl = 0

        interfering_transmitter_id = 0
        #calculate interference from other power sources
        for interfering_transmitter in self.interfering_transmitters.values():

            # if interfering_transmitter_id < 3:
            temp_line = LineString([
                (receiver.coordinates[0],
                receiver.coordinates[1]),
                (interfering_transmitter.coordinates[0],
                interfering_transmitter.coordinates[1])
                ])

            interference_strt_distance = temp_line.length

            ant_height = interfering_transmitter.ant_height
            ant_type =  'macro'

            los_distance = 250

            if interference_strt_distance < los_distance :
                type_of_sight = 'los'
            else:
                type_of_sight = 'nlos'

            building_height = 20
            street_width = 20
            type_of_sight = type_of_sight
            above_roof = 0
            indoor = receiver.indoor

            path_loss, model = path_loss_calculator(
                frequency,
                interference_strt_distance,
                ant_height,
                ant_type,
                building_height,
                street_width,
                environment,
                type_of_sight,
                receiver.ue_height,
                above_roof,
                indoor,
                seed_value,
                iterations
                )

            received_interference = self.calc_received_power(
                interfering_transmitter,
                receiver,
                path_loss
                )

            ave_distance += interference_strt_distance
            ave_pl += path_loss

            interference.append(received_interference)
            # interfering_transmitter_id += 1

            # try:
            #     ave_distance = ave_distance/len(self.interfering_transmitters)
            # except ZeroDivisionError:
            #     ave_distance = 0

            # try:
            #     ave_pl = ave_pl/len(self.interfering_transmitters)
            # except ZeroDivisionError:
            #     ave_pl = 0

            # else:
            #     break

        return interference, model, ave_distance, ave_pl


    def calculate_noise(self, bandwidth):
        """
        Terminal noise can be calculated as:

        “K (Boltzmann constant) x T (290K) x bandwidth”.

        The bandwidth depends on bit rate, which defines the number of resource blocks.
        We assume 50 resource blocks, equal 9 MHz, transmission for 1 Mbps downlink.

        Required SNR (dB)
        Detection bandwidth (BW) (Hz)
        k = Boltzmann constant
        T = Temperature (kelvins) (290 kelvin = ~16 celcius)
        NF = Receiver noise figure

        NoiseFloor (dBm) = 10log10(k*T*1000)+NF+10log10BW

        NoiseFloor (dBm) = 10log10(1.38x10e-23*290*1x10e3)+1.5+10log10(10x10e6)

        """
        k = 1.38e-23
        t = 290
        BW = bandwidth*1000000

        noise = 10*np.log10(k*t*1000)+1.5+10*np.log10(BW)

        return noise


    def calculate_sinr(self, received_power, interference, noise,
        simulation_parameters):
        """
        Calculate the Signal-to-Interference-plus-Noise-Ration (SINR).

        """
        raw_received_power = 10**received_power

        interference_list = []
        for value in interference:
            output_value = 10**value
            interference_list.append(output_value)

        interference_list.sort(reverse=True)
        interference_list = interference_list[:3]

        network_load = simulation_parameters['network_load']
        i_summed = sum(interference_list)
        raw_sum_of_interference = i_summed * (network_load/100)

        raw_noise = 10**noise

        i_plus_n = (raw_sum_of_interference + raw_noise)

        sinr = round(np.log10(
            raw_received_power / i_plus_n
            ),2)

        return received_power, raw_sum_of_interference, noise, i_plus_n, sinr


    def modulation_scheme_and_coding_rate(self, sinr,
        generation, modulation_and_coding_lut):
        """
        Uses the SINR to allocate a modulation scheme and affliated
        coding rate.

        """
        spectral_efficiency = 0.1
        for lower, upper in pairwise(modulation_and_coding_lut):
            if lower[0] and upper[0] == generation:

                lower_sinr = lower[5]
                upper_sinr = upper[5]

                if sinr >= lower_sinr and sinr < upper_sinr:
                    spectral_efficiency = lower[4]
                    return spectral_efficiency

                highest_value = modulation_and_coding_lut[-1]
                if sinr >= highest_value[5]:

                    spectral_efficiency = highest_value[4]
                    return spectral_efficiency


                lowest_value = modulation_and_coding_lut[0]

                if sinr < lowest_value[5]:

                    spectral_efficiency = 0
                    return spectral_efficiency


    def link_budget_capacity(self, bandwidth, spectral_efficiency):
        """
        Estimate site area wireless link capacity (Mbps km^2) based on
        bandwidth and receiver signal.

        capacity (Mbps km^2) = bandwidth (MHz) *
            spectral_efficiency (bps/Hz) /
            cell_area (km^2)

        """
        bandwidth_in_hertz = bandwidth * 1e6 #MHz to Hz

        link_budget_capacity_km2 = (
            (bandwidth_in_hertz * spectral_efficiency) / (self.cell_area.area / 1e6)
            )
        link_budget_capacity_mbps_km2 = link_budget_capacity_km2 / 1e6 #bps to Mbps

        return link_budget_capacity_mbps_km2


    def site_density(self):
        """
        Calculate site density per square kilometer (km^2)

        Returns
        -------
        obj
            Sum of sites

        Notes
        -----
        Function returns `0` when no sites are configered to the area.

        """
        if not self.sites:
            return 0

        sites_in_area = self.find_sites_in_area()

        postcode_sector_area = (
            [round(a.area) for a in self.area.values()]
            )[0]

        site_density = (
            len(sites_in_area) / (postcode_sector_area/1000000)
            )

        return site_density


    def receiver_density(self):
        """
        Calculate receiver density per square kilometer (km^2)

        Returns
        -------
        obj
            Sum of receiver

        Notes
        -----
        Function returns `0` when no receivers are configered to the area.
        """
        if not self.receivers:
            return 0

        postcode_sector_area = (
            [round(a.area) for a in self.area.values()]
            )[0]

        receiver_density = (
            len(self.receivers) / (postcode_sector_area/1000000)
            )

        return receiver_density


class Transmitter(object):
    """
    A site object is specific site.

    """
    def __init__(self, data, simulation_parameters):

        self.id = data['properties']['site_id']
        self.coordinates = data['geometry']['coordinates']

        self.ant_type = 'macro'
        self.ant_height = simulation_parameters['tx_baseline_height']
        self.power = simulation_parameters['tx_power']
        self.gain = simulation_parameters['tx_gain']
        self.losses = simulation_parameters['tx_losses']

    def __repr__(self):
        return "<Transmitter id:{}>".format(self.id)


class CellArea(object):
    """
    The geographic area which holds all sites and receivers.
    """
    def __init__(self, data):
        self.id = data['properties']['site_id']
        self.geometry = data['geometry']
        self.coordinates = data['geometry']['coordinates']
        self.area = self._calculate_area(data)

    def _calculate_area(self, data):
        polygon = shape(data['geometry'])
        area = polygon.area
        return area


    def __repr__(self):
        return "<Transmitter id:{}>".format(self.id)


class Receiver(object):
    """
    A receiver object is a piece of user equipment which can
    connect to a site.

    """
    def __init__(self, data, simulation_parameters):
        self.id = data['properties']['ue_id']
        self.coordinates = data['geometry']["coordinates"]

        self.misc_losses = data['properties']['misc_losses']
        self.gain = data['properties']['gain']
        self.losses = data['properties']['losses']
        self.ue_height = data['properties']['ue_height']
        self.indoor = data['properties']['indoor']

    def __repr__(self):
        return "<Receiver id:{}>".format(self.id)


class InterferingTransmitter(object):
    """
    A site object is specific site.
    """
    def __init__(self, data, simulation_parameters):

        self.id = data['properties']['site_id']
        self.coordinates = data['geometry']['coordinates']
        self.geometry = data['geometry']

        self.ant_height = simulation_parameters['tx_baseline_height']
        self.power = simulation_parameters['tx_power']
        self.gain = simulation_parameters['tx_gain']
        self.losses = simulation_parameters['tx_losses']


def transform_coordinates(old_proj, new_proj, x, y):

    new_x, new_y = transform(old_proj, new_proj, x, y)

    return new_x, new_y


def pairwise(iterable):
    """
    Return iterable of 2-tuples in a sliding window

    Parameters
    ----------
    iterable: list
        Sliding window

    Returns
    -------
    list of tuple
        Iterable of 2-tuples

    Example
    -------
        >>> list(pairwise([1,2,3,4]))
            [(1,2),(2,3),(3,4)]
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
