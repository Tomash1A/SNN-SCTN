import time
from functools import wraps
from typing import List
from scipy.interpolate import interp1d

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage import maximum_filter1d

debug = False

if not debug:
    from numba.experimental import jitclass
    from numba import njit
    from numba.typed import List as numbaList
    from numba.core.types import ListType as numbaListType
    from numba import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
    import warnings

    warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
    warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)

else:

    def njit(f):
        return f


    def jitclass(*args, **kwargs):
        def decorated_class(original_class):
            class dummy:
                def __init__(dummy_self):
                    dummy_self.instance_type = original_class

            original_class.class_type = dummy()
            return original_class

        return decorated_class


    numbaList = lambda _list: _list
    numbaListType = lambda _type: List[_type]


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f'func:{f.__name__} args:({args}, {kw}] took: {te - ts:2.4f} sec')
        return result

    return wrap


def denoise_small_values(arr, window):
    h_window = window // 2  # Half window size
    return maximum_filter1d(arr, size=window)[h_window::h_window]


@njit
def skew_score(arr):
    pivot = np.argmax(arr)
    score = 0
    for i in range(0, pivot):
        score += arr[i + 1] - arr[i]
    for i in range(pivot, len(arr) - 1):
        score += arr[i] - arr[i + 1]
    return score / arr[pivot]


def generate_filter(filter_name: str, npts):
    filter_array = np.load(f'..\\filters\\{filter_name}.npy')
    filter_array -= np.min(filter_array)
    filter_array /= np.max(filter_array)
    x = np.linspace(0, 200, len(filter_array))
    x -= x[np.argmax(filter_array)]
    x /= 4 * np.pi
    sinc = np.abs(np.sin(x)/x)
    sinc[np.argmax(filter_array)] = 1
    return sinc
    # interpolated = interp1d(np.arange(len(filter_array)), filter_array, axis=0, fill_value='extrapolate')
    # downsampled = interpolated(np.linspace(0, len(filter_array), npts))
    # return downsampled
