
import numpy as np

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


def _fit_line(x, y):
    """
    Fit a line y = mx + c
    """

    x_coordinates = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(x_coordinates, y, rcond=None)[0]
    return m, c


def calculate_residuals(x, y, model):
    """
    Calculate the errors of the model
    """

    m, c = model
    y_pred = m * x + c
    residuals = np.abs(y - y_pred)
    return residuals
