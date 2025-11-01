from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def count_color_channel_sums(image_path):
    img = Image.open(image_path).convert('RGB')
    arr = np.array(img)
    # Sum each color channel across all pixels
    red_sum = np.sum(arr[:, :, 0])
    green_sum = np.sum(arr[:, :, 1])
    blue_sum = np.sum(arr[:, :, 2])

    print("Total color channel sums:")
    print(f"red: {red_sum}")
    print(f"green: {green_sum}")
    print(f"blue: {blue_sum}")

    # Optional: plot as bar chart
    plt.bar(['red', 'green', 'blue'], [red_sum, green_sum, blue_sum], color=['red', 'green', 'blue'])
    plt.title('Total Color Channel Sums')
    plt.ylabel('Sum of Pixel Values')
    plt.show()

# Example usage:
count_color_channel_sums('img2.jpg')



