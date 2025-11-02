
import numpy as np
from random import randint

MAX_TRIALS = 100           # Number of iterations
RESIDUAL_THRESHOLD = 0.85  # Threshold to determine inliers


def fit(x, y):
    """
    Fit a line to the given data points
    """

    # defning the best model
    best_model = None

    best_inlier_count = 0
    for _ in range(MAX_TRIALS):
        # Randomly sample two points
        sample_indices = np.random.choice(len(x), 2, replace=False)
        x_sample = x[sample_indices]
        y_sample = y[sample_indices]

        # Fit a line to the sample points
        line_model = _fit_line(x_sample, y_sample)

        # Calculate residuals
        residuals = calculate_residuals(x, y, line_model)

        # Determine inliers
        inliers = residuals < RESIDUAL_THRESHOLD
        inlier_count = np.sum(inliers)

        # Update the best model if the current one is better
        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_model = line_model
    return best_model

def fit2(x, y, name):
    newx = []
    newy = []
    if name == 'x':
        values, counts = np.unique(x, return_counts=True)
        median = values[np.argmax(counts)]
        mean = np.average(x)
        overall = np.average((mean, median))
        for i, c in enumerate(x):
            if np.abs(c - overall) <= 4:
                newx.append(c)
                newy.append(y[i])
    if name == 'y':
        values, counts = np.unique(y, return_counts=True)
        median = values[np.argmax(counts)]
        mean = np.average(y)
        overall = np.average((mean, median))
        for i, c in enumerate(y):
            if np.abs(c - overall) <= 4:
                newx.append(c)
                newy.append(x[i])
    if len(newy) <= 1 or len(newy) <= 1:
        return fit(x, y)
    return fit(newx, newy)


def _fit_line(x, y):
    """
    Fit a line y = mx + c
    """

    x_coordinates = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(x_coordinates, y, rcond=None)[0]
    return m, c

def stupid_fit(x, y):
    mlist = np.zeros(250)
    clist = np.zeros(250)
    for i in range(250):
        r1 = randint(0, x.shape[0]-1)
        r2 = randint(0, x.shape[0]-1)
        while r1 == r2:
            r2 = randint(0, x.shape[0]-1)
        x1 = x[r1]
        x2 = x[r2]
        y1 = y[r1]
        y2 = y[r2]
        if x1 == x2:
            return ('x', x1)
        if y1 == y2:
            return ('y', y1)
        # c = (x2*y1 - x1*y2) / (x2-x1)
        # m = (y1-y2) / (x1-x2)
        # mlist[i] = m
        # clist[i] = c
    
    values, counts = np.unique(x, return_counts=True)
    median = values[np.argmax(counts)]
    mean = np.average(x)
    moverall = np.average((mean, median))
    values, counts = np.unique(y, return_counts=True)
    median = values[np.argmax(counts)]
    mean = np.average(y)
    coverall = np.average((mean, median))

    IQR = np.nanpercentile(x, 75) - np.nanpercentile(x, 25) 
    IQRy = np.nanpercentile(y, 75) - np.nanpercentile(y, 25) 
    if IQRy > IQR:
        return ('x', moverall)
    return ('y', coverall)

def calculate_residuals(x, y, model):
    """
    Calculate the errors of the model
    """

    m, c = model
    y_pred = m * x + c
    residuals = np.abs(y - y_pred)
    return residuals
