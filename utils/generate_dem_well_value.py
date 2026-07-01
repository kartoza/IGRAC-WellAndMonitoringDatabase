import ctypes
import gc
import math
from collections import defaultdict

import psutil
from dem_stitcher import stitch_dem
from osgeo import gdal
from rasterio.transform import rowcol

_libc = ctypes.CDLL("libc.so.6")

from gwml2.models.general import Quantity, Unit
from gwml2.models.well import Well


def _rss_mb():
    return psutil.Process().memory_info().rss / 1024 / 1024


def assign_glo_90m_elevation(wells):
    """Assign glo_90m_elevation to wells that don't have it yet.
    Wells are grouped by 1°x1° tile so each tile is downloaded once.
    """
    # Cap GDAL's block cache at 256 MB so it doesn't grow unbounded across tiles
    gdal.SetCacheMax(256 * 1024 * 1024)
    unit_m = Unit.objects.get(name='m')
    wells = wells.filter(
        glo_90m_elevation__isnull=True, location__isnull=False
    ).exclude(glo_90m_elevation_empty_result=True)

    # Group wells by their 1°x1° tile — store only IDs to avoid holding all
    # well objects in memory for the entire run.
    tiles = defaultdict(list)
    well_ids = []
    for well in wells.iterator(chunk_size=2000):
        well_ids.append(well.id)
        tile_key = f"{math.floor(well.location.x)},{math.floor(well.location.y)}"
        tiles[tile_key].append(well.id)

    if not tiles:
        print(f"assign_glo_90m_elevation - Not eligible wells")
        return Well.objects.none()

    tile_keys = list(tiles.keys())
    total_tiles = len(tile_keys)

    for tile_idx, location in enumerate(tile_keys):
        # Pop IDs from the dict so processed tiles don't linger in memory.
        tile_well_ids = tiles.pop(location)
        tile_wells = list(
            Well.objects.filter(id__in=tile_well_ids)
            .select_related('glo_90m_elevation')
        )

        lon, lat = location.split(',')
        mem_before = _rss_mb()
        print(
            f'Tile {tile_idx + 1}/{total_tiles} '
            f'({lon},{lat}) - {len(tile_wells)} well(s) | '
            f'RSS before: {mem_before:.1f} MB'
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
            del tile_wells
            continue

        # Sample elevation values directly from the numpy array via row/col
        # lookup — avoids creating a MemoryFile copy of x (~5-40 MB per tile).
        # stitch_dem may return 2D (height, width) for some tiles; normalize to 3D.
        if x.ndim == 2:
            x = x[None]
        nodata = profile.get('nodata')
        if nodata is None:
            nodata = -9999
        height, width = x.shape[1], x.shape[2]
        xs = [well.location.x for well in tile_wells]
        ys = [well.location.y for well in tile_wells]
        rows, cols = rowcol(profile['transform'], xs, ys)
        sampled = [
            x[0, max(0, min(r, height - 1)), max(0, min(c, width - 1))]
            for r, c in zip(rows, cols)
        ]

        # Free the DEM array and profile before DB writes.
        del x, profile
        gdal.VSICurlClearCache()      # evict GDAL HTTP/S3 download cache
        gc.collect()                  # close unclosed rasterio DatasetReaders
        _libc.malloc_trim(0)          # return freed heap to OS

        for well, val in zip(tile_wells, sampled):
            elevation = round(float(val), 2)
            if elevation == nodata or math.isnan(elevation):
                print(f"assign_glo_90m_elevation - Empty result for {well.id}")
                well.glo_90m_elevation_empty_result = True
                well.save(update_fields=['glo_90m_elevation_empty_result'])
                continue
            print(
                f"assign_glo_90m_elevation - Result for {well.id}: {elevation}"
            )
            if well.glo_90m_elevation:
                well.glo_90m_elevation.value = elevation
                well.glo_90m_elevation.unit = unit_m
                well.glo_90m_elevation.save(update_fields=['value', 'unit'])
            else:
                quantity = Quantity.objects.create(value=elevation, unit=unit_m)
                well.glo_90m_elevation = quantity
                well.save(update_fields=['glo_90m_elevation'])

        del tile_wells
        mem_after = _rss_mb()
        print(
            f'Tile {tile_idx + 1}/{total_tiles} done | '
            f'RSS after: {mem_after:.1f} MB | '
            f'delta: {mem_after - mem_before:+.1f} MB'
        )

    return well_ids


def assign_glo_90m_elevation_for_well(well: Well):
    """Assign glo_90m_elevation to wells that don't have it yet.
    Wells are grouped by 1°x1° tile so each tile is downloaded once.
    """
    if well.glo_90m_elevation:
        print(f"assign_glo_90m_elevation - Well already has glo_90m_elevation")
        return
    assign_glo_90m_elevation(Well.objects.filter(id=well.id))
    well.refresh_from_db()
