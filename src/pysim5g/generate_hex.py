"""

Original code written by Stephan Hügel in the Hexcover package and pretty
much lifted for use here.

See the git repo for futher details: https://github.com/urschrei/hexcover

"""
import os
import configparser
import math
import fiona
from shapely.ops import transform
from shapely.geometry import Point, mapping, shape, Polygon
from functools import partial
from rtree import index
import pyproj

from collections import OrderedDict

def convert_point_to_projected_crs(point, original_crs, new_crs):
    """

    Convert geojson point to projected coordinates.

    Parameters
    ----------
    point : dict
        Geojson point.
    original_crs : string
        Original Coordinate Reference System.
    new_crs : string
        New Coordinate Reference System.

    Returns
    -------
    output : dict
        Geojson point in desired Coordinate Reference System.

    """
    project = partial(
        pyproj.transform,
        pyproj.Proj(original_crs),
        pyproj.Proj(new_crs)
        )

    new_geom = transform(project, Point(point))

    output = {
        'type': 'Feature',
        'geometry': mapping(new_geom),
        'properties': 'Crystal Palace Radio Tower'
        }

    return output


def calculate_polygons(startx, starty, endx, endy, radius):
    """

    Calculate a grid of hexagon coordinates of the given radius
    given lower-left and upper-right coordinates. Returns a
    list of lists containing 6 tuples of x, y point coordinates.
    These can be used to construct valid regular hexagonal polygons
    Projected coordinates are advised.

    Parameters
    ----------
    startx : float
        Starting coordinate x.
    starty : float
        Starting coordinate y.
    endx : float
        Ending coordinate x.
    endy : float
        Ending coordinate y.
    radius : int
        Given radius of site areas.

    Returns
    -------
    polygons : list of lists
        A list containing multiple polygons. Each individual polygon
        is a list of tuple coordinates.

    """
    # calculate side length given radius
    sl = (2 * radius) * math.tan(math.pi / 6)

    # calculate radius for a given side-length
    # (a * (math.cos(math.pi / 6) / math.sin(math.pi / 6)) / 2)
    # see http://www.calculatorsoup.com/calculators/geometry-plane/polygon.php

    # calculate coordinates of the hexagon points
    # sin(30)
    p = sl * 0.5
    b = sl * math.cos(math.radians(30))
    w = b * 2
    h = 2 * sl

    # offset start and end coordinates by hex widths and heights to guarantee
    # coverage
    startx = startx - w
    starty = starty - h
    endx = endx + w
    endy = endy + h

    origx = startx
    origy = starty

    # offsets for moving along and up rows
    xoffset = b
    yoffset = 3 * p

    polygons = []
    row = 1
    counter = 0

    while starty < endy:

        if row % 2 == 0:
            startx = origx + xoffset

        else:
            startx = origx

        while startx < endx:
            p1x = startx
            p1y = starty + p
            p2x = startx
            p2y = starty + (3 * p)
            p3x = startx + b
            p3y = starty + h
            p4x = startx + w
            p4y = starty + (3 * p)
            p5x = startx + w
            p5y = starty + p
            p6x = startx + b
            p6y = starty
            poly = [
                (p1x, p1y),
                (p2x, p2y),
                (p3x, p3y),
                (p4x, p4y),
                (p5x, p5y),
                (p6x, p6y),
                (p1x, p1y)]

            polygons.append(poly)

            counter += 1
            startx += w

        starty += yoffset
        row += 1

    return polygons


def find_closest_site_areas(hexagons, geom_shape):
    """

    Get the transmitter and interfering site areas, by finding the closest
    hex shapes. The first closest hex shape to the transmitter will be the
    transmitter's site area. The next closest hex areas will be the
    intefering site areas.

    Parameters
    ----------
    hexagons : list of dicts
        Each haxagon is a geojson dict.
    geom_shape : Shapely geometry object
        Geometry object for the transmitter.

    Returns
    -------
    site_area : List of dicts
        Contains the geojson site area for the transmitter.
    interfering_site_areas : List of dicts
        Contains the geojson interfering site areas.

    """
    idx = index.Index()

    for site in hexagons:
        coords = site['centroid']
        idx.insert(0, coords.bounds, site)

    transmitter = mapping(geom_shape.centroid)

    site_area =  list(
        idx.nearest(
            (transmitter['coordinates'][0],
            transmitter['coordinates'][1],
            transmitter['coordinates'][0],
            transmitter['coordinates'][1]),
            1, objects='raw')
            )[0]

    closest_site_area_centroid = Polygon(
        site_area['geometry']['coordinates'][0]
        ).centroid

    all_closest_sites =  list(
        idx.nearest(
            closest_site_area_centroid.bounds,
            7, objects='raw')
            )

    interfering_site_areas = all_closest_sites[1:7]

    site_area = []
    site_area.append(all_closest_sites[0])

    return site_area, interfering_site_areas


def find_site_locations(site_area, interfering_site_areas):
    """

    Get the centroid for each site area and intefering site areas.

    Parameters
    ----------
    site_area : List of dicts
        Contains the geojson site area for the transmitter.
    interfering_site_areas : List of dicts
        Contains the geojson interfering site areas.

    Returns
    -------
    transmitter : List of dicts
        Contains the geojson site location for the transmitter.
    interfering_site_areas : List of dicts
        Contains the geojson site locations for interfering sites.

    """
    site_area_site = Polygon(
        site_area[0]['geometry']['coordinates'][0]
        ).centroid

    transmitter = []
    transmitter.append({
        'type': 'Feature',
        'geometry': mapping(site_area_site),
        'properties': {
            'site_id': 'transmitter'
        }
    })

    interfering_transmitters = []
    for interfering_site in interfering_site_areas:
        interfering_transmitters.append({
            'type': 'Feature',
            'geometry': mapping(interfering_site['centroid']),
            'properties': {
                'site_id': interfering_site['properties']['site_id']
            }
        })

    return transmitter, interfering_transmitters


def generate_site_areas(point, site_radius):
    """

    Generate a site area, as well as the interfering site areas, for
    a specific site_radius.

    Parameters
    ----------
    point : dict
        Geojson point in desired Coordinate Reference System.
    site_radius : int
        Distance between transmitter and site edge in meters.

    Returns
    -------
    site_area : List of dicts
        Contains the geojson site area for the transmitter.
    interfering_site_areas : List of dicts
        Contains the geojson interfering site areas.

    """
    geom_shape = shape(point['geometry'])

    buffered = Polygon(geom_shape.buffer(site_radius*2).exterior)

    polygon = calculate_polygons(
        buffered.bounds[0], buffered.bounds[1],
        buffered.bounds[2], buffered.bounds[3],
        site_radius)

    hexagons = []
    id_num = 0
    for poly in polygon:
        hexagons.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [poly],
            },
            'centroid': (Polygon(poly).centroid),
            'properties': {
                'site_id': id_num
                }
            })

        id_num += 1

    site_area, interfering_site_areas = find_closest_site_areas(
        hexagons, geom_shape
    )

    return site_area, interfering_site_areas


def produce_sites_and_site_areas(unprojected_point, site_radius, unprojected_crs,
    projected_crs):
    """

    Meta function to produce a set of hex shapes with a specific site_radius.

    Parameters
    ----------
    unprojected_point : Tuple
        x and y coordinates for an unprojected point.
    site_radius : int
        Distance between transmitter and site edge in meters.

    Returns
    -------
    transmitter : List of dicts
        Contains a geojson dict for the transmitter site.
    interfering_transmitters : List of dicts
        Contains multiple geojson dicts for the interfering transmitter sites.
    site_area : List of dicts
        Contains a geojson dict for the transmitter site area.
    interfering_site_areas : List of dicts
        Contains multiple geojson dicts for the interfering transmitter site
        areas.

    """
    point = convert_point_to_projected_crs(unprojected_point, unprojected_crs,
        projected_crs
    )

    site_area, interfering_site_areas = generate_site_areas(point, site_radius)

    transmitter, interfering_transmitters = find_site_locations(site_area,
        interfering_site_areas
    )

    return transmitter, interfering_transmitters, site_area, interfering_site_areas
