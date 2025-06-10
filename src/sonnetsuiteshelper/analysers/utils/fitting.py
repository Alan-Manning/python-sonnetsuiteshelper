import numpy as np


def S21_mag_fit(freqs, f0, qr, qc):
    """Fit for the S21 mag against frequency."""
    xr = freqs / f0 - 1
    s21 = 1 - ((qr / qc) * (1 / (1 + 2j * qr * xr)))
    return np.abs(s21)
