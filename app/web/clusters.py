"""Named groups of chunks, and the ellipse to draw around each one on the map.

The projection puts semantically similar chunks near each other, so a group that is
one topic is also one blob. These are the blobs the room can see; the labels are what
nobody can read off the scatter.
"""

from __future__ import annotations

import numpy as np

from rag.models import Chunk

# Car and rental documents sit far enough from the HR policies to read as their own
# blob, so "policy" alone would circle two clusters as one.
_CAR_WORDS = ("car", "rental", "renta ", "renta_", "wagens", "location-specific")

_BY_SOURCE_TYPE = {
    "cv": "CVs",
    "credit": "Credits",
    "assignment": "Credits",
    "aggregate": "Totals",
    "project": "Projects",
}

# Points beyond this percentile of their group are left outside the circle: a handful
# of strays would otherwise inflate it until it covered every other group too.
_SPREAD_PERCENTILE = 85
_PADDING = 1.15


def group_of(chunk: Chunk) -> str:
    if chunk.source_type == "policy":
        title = chunk.title.lower()
        return "Car Policy" if any(w in title for w in _CAR_WORDS) else "HR Policy"
    return _BY_SOURCE_TYPE.get(chunk.source_type, chunk.source_type)


def cluster_ellipses(
    chunks: list[Chunk], projection: np.ndarray, min_share: float = 0.05
) -> list[dict]:
    """One ellipse per group large enough to be worth naming, biggest first."""
    groups: dict[str, list[int]] = {}
    for i, chunk in enumerate(chunks):
        groups.setdefault(group_of(chunk), []).append(i)

    floor = min_share * len(chunks)
    ellipses = []
    for label, members in groups.items():
        if len(members) < floor:
            continue
        points = np.asarray(projection)[members]
        centre = np.median(points, axis=0)
        rx, ry = _PADDING * np.percentile(np.abs(points - centre), _SPREAD_PERCENTILE, axis=0)
        ellipses.append(
            {
                "label": label,
                "count": len(members),
                "x": float(centre[0]),
                "y": float(centre[1]),
                "rx": float(rx),
                "ry": float(ry),
            }
        )
    return sorted(ellipses, key=lambda e: e["count"], reverse=True)
