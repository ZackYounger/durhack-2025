import cv2
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from dspace import compute_board_pose

# Read image from file path
image_path = "img3 - edit.jpg"  # Change this to your image path
image = cv2.imread(image_path)

# Convert to NumPy array (cv2.imread already returns a NumPy array)
image_array = np.array(image)

matrix_size = 47
n = 50
h, w, _ = image_array.shape
# Create an output image initialized to black
output_image = np.zeros((3, h, w, _), dtype=image_array.dtype)

def perp( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def get_linear_intersection(array1, array2):
    nums = []
    for l,a1 in enumerate(array1):
        if l % 3 == 0:
            for f,a2 in enumerate(array1):
                if l != f and f % 3 == 0:
                    for t,b2 in enumerate(array2):
                        if t % 3 == 0:
                            for v,b1 in enumerate(array2):
                                if t != v and v % 3 == 0:
                                    da = a2-a1
                                    db = b2-b1
                                    dp = a1-b1
                                    dap = perp(da)
                                    denom = np.dot( dap, db)
                                    num = np.dot( dap, dp )
                                    nums.append((num / denom.astype(float))*db + b1)
    nums = np.array(nums)
    return (np.average(nums[:,0]), np.average(nums[:,1]))


def find_real_corners(corners, shape, colour):
    # col = np.array([255, 0, 0]).roll(colour)
    corners_ = corners[:, 0, :].astype(np.int32)
    left_line = np.zeros((shape[1], 2))
    right_line = np.zeros((shape[1], 2))
    for row in range(0, len(corners_), shape[0]):
        end = False
        x, y = corners_[row]
        while not end and x >= 0:
            pxl = np.average(inv_rgb[max(0, y-50):min(inv_rgb.shape[0], y+50), x, colour])
            if pxl < 120:
                left_line[row//shape[0]] = np.array([x,y])
                end = True
            x-=1
        x, y = corners_[row]
        end = False
        while not end and x < inv_rgb.shape[1]:
            pxl = np.average(inv_rgb[max(0, y-50):min(inv_rgb.shape[0], y+50), x, colour])
            if pxl < 120:
                right_line[row//shape[0]] = np.array([x,y])
                end = True
            x+=1

    down_line = np.zeros((shape[0], 2))
    up_line = np.zeros((shape[0], 2))
    print(inv_rgb[0])
    for column in range(round(len(corners_)*0.35), int(len(corners_)*0.65), shape[1]):
        end = False
        x, y = corners_[column]
        while not end and y >= 0:
            pxl = np.average(inv_rgb[inv_rgb[max(0, y-5):min(inv_rgb.shape[0], y+5)], max(0, x-100):min(inv_rgb.shape[1], x+100), colour])
            print(max(0, y-1),min(inv_rgb.shape[0], y+1), max(0, x-100),min(inv_rgb.shape[1], x+100), pxl)
            if pxl < 150:
                up_line[column//shape[1]] = np.array([x,y])
                end = True
            y-=1
        x, y = corners_[row]
        end = False
        while not end and y < inv_rgb.shape[0]:
            pxl = np.average(inv_rgb[inv_rgb[max(0, y-5):min(inv_rgb.shape[0], y+5)], max(0, x-50):min(inv_rgb.shape[1], x+50), colour])
            if pxl < 150:
                down_line[column//shape[1]] = np.array([x,y])
                end = True
            y+=1
    # remove all [0, 0] rows from up_line
    up_line = up_line[~np.all(up_line == 0, axis=1)]
    down_line = down_line[~np.all(down_line == 0, axis=1)]
    print(left_line)
    print(up_line)
    print(get_linear_intersection(left_line, up_line))
    return (get_linear_intersection(left_line, up_line), get_linear_intersection(left_line, down_line), get_linear_intersection(right_line, up_line), get_linear_intersection(right_line, down_line))
    




# Loop through the image in blocks of n x n pixels
for y in range(0, h, n):
    for x in range(0, w, n):
        block = image_array[y:y+n, x:x+n]
        red_sum = np.sum(block[:, :, 2])
        green_sum = np.sum(block[:, :, 1])
        blue_sum = np.sum(block[:, :, 0])
        # If green > red + blue, keep the block; else, set block to black
        if red_sum > (green_sum + blue_sum)*0.7:
            output_image[0, max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)] = image_array[max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)]
        if green_sum > (red_sum + blue_sum)*0.7:
            output_image[1, max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)] = image_array[max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)]
        if blue_sum > (green_sum + red_sum)*0.7:
            output_image[2, max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)] = image_array[max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)]

gray_r = output_image[0,..., 0]  
gray_g = output_image[1,..., 0]  
gray_b = output_image[2,..., 2]  

combined_gray = np.stack([gray_r, gray_g, gray_b], axis=0)

coords = defaultdict(dict)
order = ['red', 'green', 'blue']
colours = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]])
for i, arr in enumerate(combined_gray):
    gaus = cv2.GaussianBlur(arr, (5,5), 0)
    contour, _ = cv2.findContours(gaus, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contour:
        # Find the largest contour (assumed to be the checkered area)
        largest_contour = max(contour, key=cv2.contourArea)

        
        # Create a mask for the largest contour
        mask = np.zeros_like(arr)
        # Get bounding rect of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        x = x+round(w*0.25)
        y = y+round(h*0.25)
        w = round(w*0.5)
        h = round(h*0.5)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        roi = np.zeros_like(arr)
        roi[y:y+h, x:x+w] = arr[y:y+h, x:x+w]
        # roi = arr[y:y+h, x:x+w]
        # plt.imshow(roi, cmap='gray')
        # plt.axis('off')
        # plt.title('3D Pose Reprojection Check')
        # plt.show()
        # Define chessboard size (adjust as needed)
        chessboard_size = (20, 20)
        ret, corners = cv2.findChessboardCorners(roi, chessboard_size, None)
        while not ret:
            if chessboard_size[1] < 7:
                chessboard_size = (chessboard_size[0]-1, 20)
            else:
                chessboard_size = (chessboard_size[0], chessboard_size[1]-1)

            # Find chessboard corners in the ROI
            if (chessboard_size[0]) < 7:
                break
            ret, corners = cv2.findChessboardCorners(roi, chessboard_size, None)

        if ret:
            # Draw chessboard corners on ROI
            # print("roi shape:", roi.shape, order[i])
            # print("corners shape:", corners.shape, order[i])
            # print("chessboard_size:", chessboard_size, order[i])
            # print("rows*cols:", chessboard_size[0]*chessboard_size[1], order[i])
            # print()
            temp = image_array.copy()
            cv2.drawChessboardCorners(temp, chessboard_size, corners, ret)
            
            # Define chessboard size (adjust as needed)
            # Draw blue border around the bounding box of the chessboard
            inv_rgb = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
            points = find_real_corners(corners, chessboard_size, i)
            for i in points:
                print(i)
                # draw point on temp (convert to integer pixel coords and clamp to image bounds)
                h_t, w_t = temp.shape[:2]
                x_pt = int(round(i[0]))
                y_pt = int(round(i[1]))
                x_pt = max(0, min(w_t - 1, x_pt))
                y_pt = max(0, min(h_t - 1, y_pt))
                cv2.circle(temp, (x_pt, y_pt), 6, (0, 255, 0), -1)
            # Invert colours (and convert BGR->RGB for matplotlib)
            plt.imshow(inv_rgb)
            plt.axis('off')
            plt.title('3D Pose Reprojection Check')
            plt.show()
            dict_ = {
                'displayable image': temp,
                'coords': corners,
                'chessboard size': chessboard_size,
                '3d coords': compute_board_pose(corners, chessboard_size, 1),
                'pos': (x, y)
            }
            coords[order[i]] = dict_
