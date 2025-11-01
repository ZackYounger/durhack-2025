import cv2
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

# Read image from file path
image_path = "img1.png"  # Change this to your image path
image = cv2.imread(image_path)

# Convert to NumPy array (cv2.imread already returns a NumPy array)
image_array = np.array(image)
print(image_array)

matrix_size = 47
n = 50

h, w, _ = image_array.shape
# Create an output image initialized to black
output_image = np.zeros_like(image_array)

# Loop through the image in blocks of n x n pixels
for y in range(0, h, n):
    for x in range(0, w, n):
        block = image_array[y:y+n, x:x+n]
        red_sum = np.sum(block[:, :, 2])
        green_sum = np.sum(block[:, :, 1])
        blue_sum = np.sum(block[:, :, 0])
        # If green > red + blue, keep the block; else, set block to black
        if green_sum > (red_sum + blue_sum)*0.7:
            output_image[max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)] = image_array[max(round(y-n*0.3), 0):min(round(y+n*1.3), h), max(round(x-n*0.3), 0):min(round(x+n*1.3), w)]

# Display the output image
plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title('Blocks with Green > Red + Blue')
plt.show()