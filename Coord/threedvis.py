import cv2
import numpy as np
import matplotlib.pyplot as plt
from find_checker import coords
from camera_config import K, dist
from dspace import plot_corners_3d


def draw_remap_2d(name):
    pose = coords[name]['3d coords']
    img = coords[name]['displayable image']
    chessboard_size = coords[name]['chessboard size']


    # Assuming you already have:
    # pose = compute_board_pose(...)
    # img = the original color image of the checkerboard
    # K, dist = from calibration

    # unpack pose data
    rvec, tvec = pose['rvec'], pose['tvec']
    objp = pose['corners_3d_cam']  # or rebuild the 3D points grid if you prefer
    cols, rows = chessboard_size  # your pattern size (update to match)
    square_size = 1.0    # cm

    # (1) Rebuild the same object points in object coordinates (z=0 plane)
    obj_points = np.zeros((rows*cols, 3), np.float32)
    obj_points[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    obj_points *= square_size

    # (2) Project 3D points back into the image
    imgpts, _ = cv2.projectPoints(obj_points, rvec, tvec, K, dist)
    # (3) Draw reprojected points
    img_vis = img.copy()
    for p in imgpts.reshape(-1,2):
        cv2.circle(img_vis, tuple(np.int32(p)), 1, (255,0,0), -1)

    # (4) Optionally, draw the board coordinate axes
    axis = np.float32([[0,0,0], [3,0,0], [0,3,0], [0,0,-3]])  # 3 cm x/y/z axes
    imgpts_axis, _ = cv2.projectPoints(axis, rvec, tvec, K, dist)
    corner = tuple(np.int32(imgpts[0].ravel()))  # origin corner (0,0,0)
    img_vis = cv2.line(img_vis, corner, tuple(np.int32(imgpts_axis[1].ravel())), (255,0,0), 3)  # X (red)
    img_vis = cv2.line(img_vis, corner, tuple(np.int32(imgpts_axis[2].ravel())), (0,255,0), 3)  # Y (green)
    img_vis = cv2.line(img_vis, corner, tuple(np.int32(imgpts_axis[3].ravel())), (255,0,0), 3)  # Z (blue)

    # (5) Show result
    plt.figure(figsize=(8,6))
    plt.imshow(cv2.cvtColor(img_vis, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title('3D Pose Reprojection Check')
    plt.show()

draw_remap_2d('blue')