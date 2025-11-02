import cv2
import numpy as np
from camera_config import K, dist
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Needed for 3D plotting


def plot_corners_3d(corners_3d_cam):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    xs = corners_3d_cam[:, 0]
    ys = corners_3d_cam[:, 1]
    zs = corners_3d_cam[:, 2]
    ax.scatter(xs, ys, zs, c='b', marker='o')
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    ax.set_title('Checkerboard Corners in Camera 3D Space')
    plt.show()


def compute_board_pose(corners, pattern_size, square_size_cm, K=K, dist=dist, use_ransac=True):
    """
    corners: numpy array shape (N,1,2) from findChessboardCorners (row-major order)
    pattern_size: (cols, rows) inner corners, e.g. (18, 12)
    square_size_cm: size of each square in centimeters (float)
    K: camera matrix 3x3 (intrinsics) in pixels
    dist: distortion coefficients (None or length 4/5/8)
    use_ransac: if True, use solvePnPRansac for robustness
    Returns: dict with rvec, tvec, R, corners_3d_cam, plane_normal_cam, plane_distance_cm, reproj_error
    """
    cols, rows = pattern_size
    N = cols * rows
    assert corners.shape[0] == N, f"expected {N} corners, got {corners.shape[0]}"

    # Build object points in board coordinate system (z=0). Units = cm
    objp = np.zeros((N, 3), dtype=np.float32)
    xs, ys = np.meshgrid(np.arange(cols, dtype=np.float32),
                         np.arange(rows, dtype=np.float32))
    objp[:, 0] = xs.ravel() * square_size_cm
    objp[:, 1] = ys.ravel() * square_size_cm
    objp[:, 2] = 0.0

    image_points = corners.reshape(-1, 2).astype(np.float32)
    objp = np.ascontiguousarray(objp, dtype=np.float32)
    image_points = np.ascontiguousarray(image_points, dtype=np.float32).reshape(-1, 1, 2)
    
    # Solve PnP with fallback strategy
    success = False
    inliers = None
    
    if use_ransac:
        success, rvec, tvec, inliers = cv2.solvePnPRansac(
            objp, image_points, K, dist,
            flags=cv2.SOLVEPNP_ITERATIVE,
            reprojectionError=15.0,  # Increased tolerance for distorted images
            iterationsCount=500,      # More iterations
            confidence=0.95           # Slightly lower confidence
        )
        # print(f"RANSAC success: {success}")
    
    # Fallback to regular solvePnP if RANSAC fails
    if not success:
        print("RANSAC failed, trying regular solvePnP...")
        success, rvec, tvec = cv2.solvePnP(
            objp, image_points, K, dist, 
            flags=cv2.SOLVEPNP_ITERATIVE,
            useExtrinsicGuess=False
        )
        inliers = np.arange(len(objp)).reshape(-1, 1)
        print(f"solvePnP success: {success}")

    if not success:
        raise RuntimeError("Both solvePnPRansac and solvePnP failed")

    # Rotation matrix
    R, _ = cv2.Rodrigues(rvec)

    # 3D positions of all object points in camera coordinates (cm)
    corners_3d_cam = (R @ objp.T).T + tvec.reshape(1, 3)

    # plane normal in camera frame
    normal_cam = R[:, 2]
    normal_cam_unit = normal_cam / np.linalg.norm(normal_cam)

    # distance from camera origin to plane
    plane_distance_cm = float(np.dot(normal_cam_unit, tvec.flatten()))

    # reprojection error
    projected, _ = cv2.projectPoints(objp, rvec, tvec, K, dist)
    projected = projected.reshape(-1, 2)
    err = np.linalg.norm(projected - image_points.reshape(-1, 2), axis=1)
    reproj_error = float(np.sqrt((err**2).mean()))


    return {
        "rvec": rvec.reshape(3,),
        "tvec": tvec.reshape(3,),
        "R": R,
        "corners_3d_cam": corners_3d_cam,
        "normal_cam": normal_cam_unit,
        "plane_distance_cm": plane_distance_cm,
        "reprojection_error_px": reproj_error,
        "inliers": inliers
    }
