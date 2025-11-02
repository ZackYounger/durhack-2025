from find_checker import coords
import numpy as np
from dspace import plot_corners_3d

stacked = np.vstack([
    coords['red']['3d coords']['corners_3d_cam'],
    coords['green']['3d coords']['corners_3d_cam'],
    coords['blue']['3d coords']['corners_3d_cam']
])

plot_corners_3d(stacked)