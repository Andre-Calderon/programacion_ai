"""Select measurement rounds by temperature."""

import numpy as np

from measurements.processing import FloatArray, validate_shape


def select_warm_rounds(readings: FloatArray, threshold: float) -> FloatArray:
    """Return the complete rounds whose north room is at or above the threshold."""
    validate_shape(readings)
    if not np.isfinite(readings).all():
        raise ValueError("Readings must be finite")
    if not np.isfinite(threshold):
        raise ValueError("Threshold must be finite")
    warm_rounds = readings[:, 0] >= threshold
    # A boolean mask creates a copy, so the input array is never modified.
    return readings[warm_rounds]
