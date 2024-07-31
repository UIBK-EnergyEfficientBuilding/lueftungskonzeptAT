
import numpy as np

#https://stackoverflow.com/questions/18915378/rounding-to-significant-figures-in-numpy
def signif(x, p):
    x = np.asarray(x)
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags

def result_stats(value,precision=3):
    mean = signif(np.mean(value),precision)
    q = np.quantile(value,[0.05, 0.25, 0.5, 0.75, 0.95])
    error = signif((q[-1] - q[0])/2,precision)
    q = signif(q,precision)
    return {"mean": mean, "error": error, "median":q[2], "quantiles":q}

def result_stats_integer(value):
    q = np.quantile(value,[0.05, 0.25, 0.5, 0.75, 0.95])
    return {"min": np.min(value), "max": np.max(value), "quantiles":q.astype(int)}

def cum_mean(arr):
    cum_sum = np.cumsum(arr, axis=0)
    deno = np.arange(1,cum_sum.shape[0]+1)
    return cum_sum/deno

def movavg(arr):
    cum_sum = np.cumsum(arr, axis=1)
    deno = np.tile(np.arange(1,arr.shape[1]+1),(arr.shape[0],1))
    return cum_sum/deno

def quantile_pos(arr,q):
    arr_q = np.quantile(arr, q, axis=0)
    q_idx=abs(arr[:,-1].reshape(-1,1)-arr_q[:,-1].reshape(1,-1)).argmin(axis=0)
    return arr_q, q_idx

def castorfalse(value,t):
    if value is None:
        return True
    try:
        t(value)
        return True
    except ValueError:
        return False
    
def find_nearest(array, value):     #from chatGPT, not tested
    """
    Find the elements in the array nearest to the given value.

    Parameters:
        array (numpy.ndarray): Input array.
        value (float or int): Target value.

    Returns:
        nearest_elements (numpy.ndarray): Array elements nearest to the target value.
    """
    # Calculate absolute differences between array elements and the target value
    absolute_differences = np.abs(array - value)
    
    # Find the index of the minimum absolute difference
    index_min = np.argmin(absolute_differences)
    
    # Return the array element(s) nearest to the target value
    return array[index_min]
