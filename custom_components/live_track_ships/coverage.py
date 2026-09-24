"""How much of a requested circle a source can actually see (SSOT item 249).

⚠ BarentsWatch clips every vessel to its published open area
(`v1/openaisarea`, a GeoJSON MultiPolygon). Measured 2026-09-23: 0 of 1,681
rows fell outside it, and its southern edge crosses the Skagerrak - Skagen,
Gothenburg, Aarhus and Hamburg are all outside. A circle reaching past it
shows empty water there forever, and nothing on the map says why. This lets
the config flow say so before the entry is created.

Pure standard library, so it is testable without Home Assistant. The area
has about 19,000 vertices; call outside_share() in an executor.
"""

from __future__ import annotations

import math

KM_PER_DEG_LAT = 111.32


def _in_ring(x: float, y: float, ring) -> bool:
    """Ray casting. Ring points are [lon, lat], GeoJSON order."""
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def in_area(lat: float, lon: float, geometry: dict) -> bool:
    """True if the point is inside a GeoJSON Polygon or MultiPolygon.
    A point inside a hole is outside."""
    kind = geometry.get("type")
    coords = geometry.get("coordinates") or []
    polygons = [coords] if kind == "Polygon" else coords if kind == "MultiPolygon" else []
    for poly in polygons:
        if not poly:
            continue
        if _in_ring(lon, lat, poly[0]) and not any(
                _in_ring(lon, lat, hole) for hole in poly[1:]):
            return True
    return False


def sample_points(lat: float, lon: float, radius_km: float, per_side: int = 15):
    """An even grid over the circle, clipped to it. per_side 15 gives ~177
    points - coarse, which is the point: the answer is a share to warn about,
    not a boundary to draw."""
    dlat = radius_km / KM_PER_DEG_LAT
    dlon = radius_km / (KM_PER_DEG_LAT * max(math.cos(math.radians(lat)), 0.01))
    pts = []
    for i in range(per_side):
        for k in range(per_side):
            fy = -1 + 2 * (i + 0.5) / per_side
            fx = -1 + 2 * (k + 0.5) / per_side
            if fx * fx + fy * fy <= 1.0:
                pts.append((lat + fy * dlat, lon + fx * dlon))
    return pts


def outside_share(lat: float, lon: float, radius_km: float,
                  geometry: dict | None) -> float | None:
    """Share of the circle (0.0-1.0) outside the source's area, or None when
    the area is unknown - an unknown area is never reported as a gap."""
    if not geometry or geometry.get("type") not in ("Polygon", "MultiPolygon"):
        return None
    pts = sample_points(lat, lon, radius_km)
    if not pts:
        return None
    out = sum(1 for p in pts if not in_area(p[0], p[1], geometry))
    return out / len(pts)
