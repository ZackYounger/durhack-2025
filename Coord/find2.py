import cv2
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from dspace import compute_board_pose
from ransac import fit

# Read image from file path
image_path = "lule.jpg"  # Change this to your image path
image = cv2.imread(image_path)

# Convert to NumPy array (cv2.imread already returns a NumPy array)
image_array = np.array(image)

matrix_size = 47
n = 50
h, w, _ = image_array.shape

new_img = np.zeros_like(image_array)
def leeway_w(a, b):
    return int(min(max(0, a + b), w-1))
def leeway_h(a, b):
    return int(min(max(0, a + b), h-1))


def getcorners(colour):
    meanx = 0
    meany = 0
    counter = 0

    for y in range(0, h, n):
        for x in range(0, w, n):
            # print(2*np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),colour]), np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),colour]) + np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),colour]))
            if 0.7*np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),colour]) > np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 2) % 3]) + np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 1) % 3]) :
                new_img[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5)] = image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5)]
                meanx += x + n/2
                meany += y + n/2
                counter += 1
    edges = [[] for i in range(4)]
    meanx, meany = int(meanx/counter), int(meany/counter)
    print(meanx, meany)

    for i in range(6):
        y = n + meany - int(i * n / 3)
        x = meanx
        while x >= 0:
            if np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), x, colour]) <  np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), x,(colour + 1) % 3]) + np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), x,(colour + 2) % 3]):
                edges[0].append(((x, y)))
                break
            x -= 1
    
    for i in range(6):
        y = n + meany - int(i * n / 3)
        x = meanx
        while x < w:
            if np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), x, colour]) <  np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), x,(colour + 1) % 3]) + np.average(image_array[leeway_h(y, -n*0.5):leeway_h(y+n, n*0.5), x,(colour + 2) % 3]):
                edges[1].append(((x, y)))
                break
            x += 1

    for i in range(6):
        y = meany
        x = n + meanx - int(i * n / 3)
        while y >= 0:
            if np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5), colour]) <  np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 1) % 3]) + np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 2) % 3]):
                # print(0.3*np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5), colour]), np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 1) % 3]) + np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 2) % 3]))
                edges[2].append(((x, y)))
                break
            y -= 1
    
    for i in range(6):
        y = meany
        x = n + meanx - int(i * n / 3)
        while y < h:
            if np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5), colour]) <  np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 1) % 3]) + np.average(image_array[y, leeway_w(x, -n*0.5):leeway_w(x+n, n*0.5),(colour + 2) % 3]):
                edges[3].append(((x, y)))
                break
            y += 1
    print(edges)
    for i in edges:
        for p in i:
            cv2.circle(new_img, p, radius=20, color=(255, 255, 255), thickness=3)
    coefficients = []
    edges2 = []
    edges2.append(edges[2])
    edges2.append(edges[1])
    edges2.append(edges[3])
    edges2.append(edges[0])
    temp = np.array(edges2)
    
    for m in range(4):
        best_model = fit(temp[m,:,0], temp[m,:,1]) # Fit a line to the points
        slope, intercept = best_model          # Get the slope and intercept of the line
        coefficients.append((slope, intercept))


    # Calculate the intersection of the lines
    intersections = []
    for f in range(2):
        for v in range(2):
            x = (coefficients[v * 2][1] -
                coefficients[f * 2 + 1][1]) / (coefficients[f * 2 + 1][0] -
                coefficients[v * 2][0])
            y = coefficients[f * 2 + 1][0] * x + coefficients[f * 2 + 1][1]
            intersections.append((round(x), round(y)))
    for i in range(4):
        for i in range(4):
            p1 = tuple(map(int, intersections[i]))
            p2 = tuple(map(int, intersections[(i + 1) % 4]))
            cv2.line(image_array, p1, p2, color=(255, 255, 255), thickness=3)
            # cv2.circle(image_array, p1, radius=6, color=(0, 0, 255), thickness=-1)
    cv2.circle(image_array, (meanx, meany), radius=20, color=(255, 255, 255), thickness=3)
    print(intersections)
    print(coefficients)
    plt.imshow(image_array)
    plt.axis('off')
    plt.title('3D Pose Reprojection Check')
    plt.show()

getcorners(2)