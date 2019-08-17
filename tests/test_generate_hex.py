import pytest
from shapely.geometry import shape
from pysim5g.generate_hex import produce_sites_and_site_areas

def test_produce_sites_and_site_areas(setup_unprojected_point, setup_inter_site_distance,
    setup_unprojected_crs, setup_projected_crs):

    transmitter, interfering_transmitters, site_area, interfering_site_areas = \
        produce_sites_and_site_areas(setup_unprojected_point['geometry']['coordinates'],
        setup_inter_site_distance[0], setup_unprojected_crs, setup_projected_crs)

    actual_site_area_km2 = round(shape(site_area[0]['geometry']).area / 1e6, 1)
    actual_interfering_site_area_km2 = round(
        shape(interfering_site_areas[0]['geometry']).area / 1e6, 1
    )

    assert actual_site_area_km2 == 0.2
    assert actual_interfering_site_area_km2 == 0.2


    transmitter, interfering_transmitters, site_area, interfering_site_areas = \
        produce_sites_and_site_areas(setup_unprojected_point['geometry']['coordinates'],
        setup_inter_site_distance[1], setup_unprojected_crs, setup_projected_crs)

    actual_site_area_km2 = round(shape(site_area[0]['geometry']).area / 1e6, 1)
    actual_interfering_site_area_km2 = round(
        shape(interfering_site_areas[0]['geometry']).area / 1e6, 1
    )
    assert actual_site_area_km2 == round(779422863 / 1e6, 1)
    assert actual_interfering_site_area_km2 == round(779422863 / 1e6, 1)
