
import numpy as np

#https://stackoverflow.com/questions/18915378/rounding-to-significant-figures-in-numpy
def signif(x, p):
    x = np.asarray(x)
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags

def result_stats(value,precision=2):
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

def castorfalse(value,t):
    if value is None:
        return True
    try:
        t(value)
        return True
    except ValueError:
        return False
