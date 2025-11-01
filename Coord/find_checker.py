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
gray_g = output_image[1,..., 0]  
gray_b = output_image[2,..., 2]  

combined_gray = np.stack([gray_r, gray_g, gray_b], axis=0)

# Show the grayscale image
# for i in combined_gray:
#     plt.imshow(i, cmap='gray')
#     plt.axis('off')
#     plt.title('Grayscale Output Image')
#     plt.show()
for i, arr in enumerate(combined_gray):
    # _, thresh = cv2.threshold(arr, 1, 255, cv2.THRESH_BINARY)
    gaus = cv2.GaussianBlur(arr, (5,5), 0)
    contour, _ = cv2.findContours(gaus, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contour:
        # Find the largest contour (assumed to be the checkered area)
        largest_contour = max(contour, key=cv2.contourArea)
        print(largest_contour.shape)
        print(arr.shape)
        # Create a mask for the largest contour
        mask = np.zeros_like(arr)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        # Get bounding rect of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        x = x+round(w*0.25)
        y = y+round(h*0.25)
        w = round(w*0.5)
        h *= round(h*0.5)
        roi = output_image[i, y:y+h, x:x+w]
        plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.title('ROI')
        plt.show()
        roi_mask = mask[y:y+h, x:x+w]
        # Apply mask to ROI
        roi_gray = roi[..., min(i+1, 2)]
        print(roi_gray.shape)
        # roi_gray = cv2.bitwise_and(roi_gray, roi_mask)
        plt.imshow(roi_gray, cmap='gray')
        plt.axis('off')
        plt.title('roi_gray22222')
        plt.show()
        # plt.imshow(roi_gray, cmap='gray')
        # plt.hist(roi_gray.ravel(), 256)
        # plt.show()

        # Define chessboard size (adjust as needed)
        chessboard_size = (20, 20)
        ret, corners = cv2.findChessboardCorners(roi_gray, chessboard_size, None)
        while not ret:
            if chessboard_size[1] < 7:
                chessboard_size = (chessboard_size[0]-1, 20)
            else:
                chessboard_size = (chessboard_size[0], chessboard_size[1]-1)

            print(chessboard_size)
            # Find chessboard corners in the ROI
            if (chessboard_size[0]) < 7:
                break
            ret, corners = cv2.findChessboardCorners(roi_gray, chessboard_size, None)
        print(chessboard_size, end='\n\n')

        if ret:
            # Draw chessboard corners on ROI
            print("roi shape:", roi.shape)
            print("roi_gray shape:", roi_gray.shape)
            print("corners shape:", corners.shape)
            print("chessboard_size:", chessboard_size)
            print("rows*cols:", chessboard_size[0]*chessboard_size[1])
            cv2.drawChessboardCorners(roi, chessboard_size, corners, ret)
            # Draw blue border around the bounding box of the chessboard
            cv2.rectangle(output_image[i], (x, y), (x+w, y+h), (255, 0, 0), 5)
            plt.imshow(cv2.cvtColor(output_image[i], cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.title('Chessboard in Largest Contour (Bordered Blue)')
            plt.show()