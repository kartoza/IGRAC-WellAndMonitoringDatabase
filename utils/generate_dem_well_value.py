import math
from collections import defaultdict

import rasterio
from dem_stitcher import stitch_dem

from gwml2.models.general import Quantity, Unit
from gwml2.models.well import Well


def assign_glo_90m_elevation(wells):
    """Assign glo_90m_elevation to wells that don't have it yet.
    Wells are grouped by 1°x1° tile so each tile is downloaded once.
    """
    unit_m = Unit.objects.get(name='m')
    wells = wells.filter(
        glo_90m_elevation__isnull=True, location__isnull=False
    ).exclude(glo_90m_elevation_empty_result=True)

    if not wells.count():
        print(f"assign_glo_90m_elevation - No eligible wells")
        return Well.objects.none()
    print(f"assign_glo_90m_elevation - run for {len(wells)} wells")

    # Group wells by their 1°x1° tile (floor of lon/lat)
    tiles = defaultdict(list)
    for well in wells:
        lon = well.location.x
        lat = well.location.y
        tile_key = f"{math.floor(lon)},{math.floor(lat)}"
        tiles[tile_key].append(well)

    total_tiles = len(tiles)
    for tile_idx, (location, tile_wells) in enumerate(tiles.items()):
        lon, lat = location.split(',')
        print(
            f'Tile {tile_idx + 1}/{total_tiles} '
            f'({lon},{lat}) - {len(tile_wells)} well(s)'
        )

        # Create bounds for the tile
        bounds = [int(lon), int(lat), int(lon) + 1, int(lat) + 1]
        try:
            x, profile = stitch_dem(
                bounds,
                dem_name='glo_90',
                dst_ellipsoidal_height=False,
                dst_area_or_point='Point'
            )
        except Exception as e:
            print(f'Failed to download tile: {e}')
            continue

        # Open profile using rasterio in memory
        # After that sample it
        with rasterio.MemoryFile() as memory:
            with memory.open(**profile) as datasets:
                datasets.write(x, 1)
                coords = [
                    (well.location.x, well.location.y) for well in tile_wells
                ]
                sampled = list(datasets.sample(coords))

        for well, val in zip(tile_wells, sampled):
            elev = round(float(val[0]), 2)
            if elev == profile.get('nodata', -9999) or math.isnan(elev):
                print(
                    'assign_glo_90m_elevation - '
                    f'Well {well.pk}: no DEM value, skipping'
                )
                well.glo_90m_elevation_empty_result = True
                well.save(update_fields=['glo_90m_elevation_empty_result'])
                continue
            quantity = Quantity.objects.create(value=elev, unit=unit_m)
            well.glo_90m_elevation = quantity
            well.save(update_fields=['glo_90m_elevation'])

    return wells


def assign_glo_90m_elevation_for_well(well: Well):
    """Assign glo_90m_elevation to wells that don't have it yet.
    Wells are grouped by 1°x1° tile so each tile is downloaded once.
    """
    if well.glo_90m_elevation:
        print(f"assign_glo_90m_elevation - Well already has glo_90m_elevation")
        return
    assign_glo_90m_elevation(Well.objects.filter(id=well.id))
