import cv2
import numpy as np
import matplotlib.pyplot as plt
from .ransac import fit2, _fit_line, stupid_fit

# Read image from file path
image_path = "Coord/test.jpg"  # Change this to your image path
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
    if counter == 0:
        return 0
    edges = [[] for i in range(4)]
    meanx, meany = int(meanx/counter), int(meany/counter)

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
    for i in edges:
        for p in i:
            cv2.circle(image_array, p, radius=20, color=(255, 255, 255), thickness=3)
    coefficients = []
    edges2 = []

    edges2.append(edges[1])
    edges2.append(edges[3])
    edges2.append(edges[0])
    edges2.append(edges[2])
    temp = np.array(edges2)
    
    for m in range(4):
        # best_model = fit2(temp[m,:,0], temp[m,:,1], 'y') if m % 2 == 0 else  fit2(temp[m,:,0], temp[m,:,1], 'x')
        best_model = stupid_fit(temp[m,:,0], temp[m,:,1], )
        coefficients.append(best_model)

    for i in range(4):
        if coefficients[i][0] == 'x':
            cv2.line(image_array, (int(coefficients[i][1]), 0), (int(coefficients[i][1]), h), color=(255, 255, 255), thickness=3)
        if coefficients[i][0] == 'y':
            cv2.line(image_array, (0, int(coefficients[i][1])), (w, int(coefficients[i][1])), color=(255, 255, 255), thickness=3)
    
    x_vals = [c for s, c in coefficients if s == 'x']
    y_vals = [c for s, c in coefficients if s == 'y']

    coords = [[int(x), int(y)] for x in x_vals for y in y_vals]
    return coords

red = sorted(getcorners(2))
green = getcorners(1)
blue = getcorners(0)
origin = red[0]

if red:
    red.sort()
    if len(red) > 1:
        # # draw polyline through the red points and close the loop
        # pts = [ (int(x), int(y)) for x,y in red ]
        # for i in range(len(pts)):
        #     p1 = pts[i]
        #     p2 = pts[(i+1) % len(pts)]
        #     cv2.line(image_array, p1, p2, color=(0,0,255), thickness=2)
    for i in range(len(red)):
        red[i] = (red[i][0] - origin[0], red[i][1] - origin[1])

    
if green:
    green.sort()
    for i in range(len(green)):
        green[i] = (green[i][0] - origin[0], green[i][1] - origin[1])

if blue:
    blue.sort()
    for i in range(len(blue)):
        blue[i] = (blue[i][0] - origin[0], blue[i][1] - origin[1])

def coords():
    return {
        'red': red,
        'green': green,
        'blue': blue,
    }

# print(coords())