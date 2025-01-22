from pathlib import Path

import numpy as np
import pandas as pd


def strip_trailing_nans(arr: np.ndarray) -> np.ndarray:
    """Remove trailing NaNs from a 2D numpy array.
    
    Only removes NaNs if they are at the end of columns.
    
    Parameters
    ----------
    arr : np.ndarray
        Array to strip.
    
    Returns
    -------
    np.ndarray
        2D numpy array with trailing NaNs removed.
    """
    # Find last non-NaN index in each row
    last_valid = np.maximum.accumulate(
        np.where(~np.isnan(arr), np.arange(arr.shape[1]), 0),
        axis=1
    )
    
    # Find maximum needed width by finding the rightmost non-NaN value
    max_width = last_valid.max() + 1
    
    # Return trimmed array
    return arr[:, :max_width]

def read_ascii(
    file_000: Path, file_090: Path, file_ver: Path
) -> tuple[float, np.ndarray]:
    """
    Read ASCII waveform files (000, 090, vertical) and return the sampling interval (dt) and waveform data.

    Parameters
    ----------
    file_000 : Path
        Path to the 000 component file.
    file_090 : Path
        Path to the 090 component file.
    file_ver : Path
        Path to the vertical component file.

    Returns
    -------
    Tuple[float, np.ndarray]
        Sampling interval (dt) and waveform data as a NumPy array.
    """
    # Load all components
    comp_000 = pd.read_csv(file_000, sep=r"\s+", header=None, skiprows=2).values.ravel()
    comp_090 = pd.read_csv(file_090, sep=r"\s+", header=None, skiprows=2).values.ravel()
    comp_ver = pd.read_csv(file_ver, sep=r"\s+", header=None, skiprows=2).values.ravel()
    waveform_data = strip_trailing_nans(np.stack((comp_000, comp_090, comp_ver), axis=1).T).T

    # Extract the sampling interval (dt) from the 000 component file
    delta = pd.read_csv(file_000, sep=r"\s+", header=None, nrows=2, skiprows=1).iloc[
        0, 1
    ]

    if np.any(np.isnan(comp_000) | np.isnan(comp_090) | np.isnan(comp_ver)):
        raise ValueError('Components contain NaN values.')

    # Ensure dtype is float 32
    waveform_data = waveform_data.astype(np.float32)

    # Reshape the waveform to have the correct shape for the IM calculation
    reshaped_waveform = waveform_data[np.newaxis, :, :]

    return delta, reshaped_waveform
