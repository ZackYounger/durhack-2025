import cv2
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

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
gray_g = output_image[1,..., 1]  
gray_b = output_image[2,..., 2]  

combined_gray = np.stack([gray_r, gray_g, gray_b], axis=0)

# Show the grayscale image
# for i in combined_gray:
#     plt.imshow(i, cmap='gray')
#     plt.axis('off')
#     plt.title('Grayscale Output Image')
#     plt.show()

_, thresh_r = cv2.threshold(gray_r, 1, 255, cv2.THRESH_BINARY)
_, thresh_g = cv2.threshold(gray_r, 1, 255, cv2.THRESH_BINARY)
_, thresh_b = cv2.threshold(gray_r, 1, 255, cv2.THRESH_BINARY)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    # Find the largest contour (assumed to be the checkered area)
    largest_contour = max(contours, key=cv2.contourArea)
    # Create a mask for the largest contour
    mask = np.zeros_like(gray_r)
    cv2.drawContours(mask, [largest_contour], -1, 255, -1)
    # Get bounding rect of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    x = x+round(w*0.25)
    y = y+round(h*0.25)
    w = round(w*0.5)
    h *= round(h*0.5)
    roi = output_image[y:y+h, x:x+w]
    roi_mask = mask[y:y+h, x:x+w]
    # Apply mask to ROI
    roi_gray = roi[..., 0]  
    plt.imshow(roi_gray, cmap='gray')
    plt.axis('off')
    plt.title('roi_gray')
    plt.show()
    roi_gray = cv2.bitwise_and(roi_gray, roi_mask)
    plt.imshow(roi_gray, cmap='gray')
    plt.axis('off')
    plt.title('roi_gray22222')
    plt.show()

    # Define chessboard size (adjust as needed)
    chessboard_size = (16, 16)
    ret, corners = cv2.findChessboardCorners(roi_gray, chessboard_size, None)
    while not ret:
        chessboard_size = (chessboard_size[0]-1, chessboard_size[1]-1)
        # Find chessboard corners in the ROI
        ret, corners = cv2.findChessboardCorners(roi_gray, chessboard_size, None)

    if ret:
        # Draw chessboard corners on ROI
        cv2.drawChessboardCorners(roi, chessboard_size, corners, ret)
        # Draw blue border around the bounding box of the chessboard
        cv2.rectangle(output_image, (x, y), (x+w, y+h), (255, 0, 0), 5)
        plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.title('Chessboard in Largest Contour (Bordered Blue)')
        plt.show()