from PIL import Image
import numpy as np
import random
import argparse

def clamp01(value):
    return min(1, max(value, 0))

def valid(dim, corner):
    return corner[0] >= 0 and corner[0] < dim and corner[1] >= 0 and corner[1] < dim

def diamondsquare(data, dim, roughness):
    roughness = clamp01(roughness)
    data[0][0] = random.uniform(-1, 1)
    data[dim - 1][0] = random.uniform(-1, 1)
    data[0][dim - 1] = random.uniform(-1, 1)
    data[dim - 1][dim - 1] = random.uniform(-1, 1)

    level = 0
    step = dim - 1
    strength = 1
    while step > 1:
        strength *= pow(2, -roughness)
        halfstep = step >> 1
        for i in range(1 << level):
            for j in range(1 << level):
                x = i * step
                y = j * step
                value = 0
                corners = [(x, y), (x + step, y), (x, y + step), (x + step, y + step)]
                center = (x + halfstep, y + halfstep)
                for corner in corners:
                    value += data[corner[0]][corner[1]]
                value = 0.25 * value + strength * random.uniform(-1.0, 1.0)
                data[center[0]][center[1]] = value
                
                midpoints = [(x + halfstep, y), (x, y + halfstep), (x + step, y + halfstep), (x + halfstep, y + step)]
                dcorners = [list(filter(lambda c: valid(dim, c), [(p[0], p[1] - halfstep), (p[0] - halfstep, p[1]), (p[0] + halfstep, p[1]), (p[0], p[1] + halfstep)])) for p in midpoints]
                for index, diamond in enumerate(dcorners):
                    value = 0
                    for c in diamond:
                        value += data[c[0]][c[1]]
                    data[midpoints[index][0]][midpoints[index][1]] = value / len(diamond) + strength * random.uniform(-1.0, 1.0)
        step = step >> 1
        level += 1

def generate(power, roughness):
    dim = (1 << power) + 1
    heightmap = np.zeros((dim, dim), dtype=np.float32)
    diamondsquare(heightmap, dim, roughness)
    return heightmap

def to_png(filename, heightmap):
    minheight = np.min(heightmap)
    maxheight = np.max(heightmap)

    dim = len(heightmap)
    image = np.zeros((dim, dim, 3), dtype=np.uint8)
    for y in range(0, dim):
        for x in range(0, dim):
            value = np.uint8(255.0 * clamp01((heightmap[x][y] - minheight) / (maxheight - minheight)))
            image[x][y][0] = value
            image[x][y][1] = value
            image[x][y][2] = value
    Image.fromarray(image).save(filename)

parser = argparse.ArgumentParser(prog='py run.py', description='Generate heightmap', usage='%(prog)s [options]')
parser.add_argument('power', type=int, help='the power used to calculate image size as 2^power + 1')
parser.add_argument('roughness', type=float, help='roughness value clamped in range [0,1] (lower means rougher)')

try:
    args = parser.parse_args()
    to_png("image.png", generate(args.power, args.roughness))
except argparse.ArgumentError:
    parser.print_help()