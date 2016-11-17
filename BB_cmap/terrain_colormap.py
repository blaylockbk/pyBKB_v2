## Custom Terrain ColorMaps by Brian

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

## Terrain Color Map created using http://colormap.org/

def terrain_cmap_256():
    """
    Custom terrain colormap with 256 distinct colors.
    """
    C = np.array([[0, 0, 255], 
                  [2, 97, 0],  # Alternativley [0, 0, 255], for blue at sealevel
                  [2, 97, 0],
                  [3, 97, 0],
                  [4, 97, 0],
                  [5, 97, 0],
                  [6, 98, 0],
                  [7, 98, 0],
                  [8, 98, 0],
                  [9, 98, 0],
                  [10, 98, 0],
                  [11, 98, 0],
                  [11, 99, 0],
                  [12, 99, 0],
                  [13, 99, 0],
                  [14, 99, 0],
                  [15, 99, 0],
                  [16, 99, 0],
                  [17, 100, 0],
                  [18, 100, 0],
                  [19, 100, 0],
                  [19, 100, 0],
                  [20, 100, 0],
                  [21, 101, 0],
                  [22, 101, 0],
                  [23, 101, 0],
                  [24, 101, 0],
                  [25, 101, 0],
                  [26, 102, 0],
                  [27, 102, 0],
                  [28, 102, 0],
                  [28, 102, 0],
                  [29, 102, 0],
                  [30, 102, 0],
                  [31, 103, 0],
                  [32, 103, 0],
                  [33, 103, 0],
                  [34, 103, 0],
                  [35, 103, 0],
                  [36, 104, 0],
                  [37, 104, 0],
                  [37, 104, 0],
                  [38, 104, 0],
                  [39, 104, 0],
                  [40, 104, 0],
                  [41, 105, 0],
                  [42, 105, 0],
                  [43, 105, 0],
                  [44, 105, 0],
                  [45, 105, 0],
                  [45, 106, 0],
                  [46, 106, 0],
                  [47, 106, 0],
                  [48, 106, 0],
                  [49, 106, 0],
                  [50, 106, 0],
                  [51, 107, 0],
                  [52, 107, 0],
                  [53, 107, 0],
                  [54, 107, 0],
                  [54, 107, 0],
                  [55, 108, 0],
                  [56, 108, 0],
                  [57, 108, 0],
                  [58, 108, 0],
                  [59, 108, 0],
                  [60, 108, 1],
                  [61, 109, 1],
                  [62, 109, 2],
                  [63, 109, 2],
                  [64, 109, 3],
                  [65, 109, 3],
                  [66, 110, 4],
                  [67, 110, 4],
                  [68, 110, 4],
                  [69, 110, 5],
                  [70, 110, 5],
                  [71, 110, 6],
                  [72, 111, 6],
                  [73, 111, 7],
                  [74, 111, 7],
                  [75, 111, 8],
                  [76, 111, 8],
                  [77, 112, 9],
                  [78, 112, 9],
                  [79, 112, 10],
                  [80, 112, 10],
                  [81, 112, 11],
                  [82, 112, 11],
                  [83, 113, 12],
                  [84, 113, 12],
                  [85, 113, 13],
                  [85, 113, 13],
                  [86, 113, 14],
                  [87, 114, 14],
                  [88, 114, 15],
                  [89, 114, 15],
                  [90, 114, 16],
                  [91, 114, 16],
                  [92, 114, 17],
                  [93, 115, 17],
                  [94, 115, 18],
                  [95, 115, 18],
                  [96, 115, 19],
                  [97, 115, 19],
                  [98, 115, 20],
                  [99, 116, 20],
                  [100, 116, 20],
                  [101, 116, 21],
                  [102, 116, 21],
                  [103, 116, 22],
                  [104, 117, 22],
                  [105, 117, 23],
                  [106, 117, 23],
                  [107, 117, 24],
                  [108, 117, 24],
                  [109, 118, 25],
                  [110, 118, 25],
                  [111, 118, 26],
                  [112, 118, 26],
                  [113, 118, 27],
                  [114, 118, 27],
                  [115, 119, 28],
                  [116, 119, 28],
                  [117, 119, 29],
                  [118, 119, 29],
                  [119, 119, 30],
                  [120, 120, 30],
                  [121, 120, 31],
                  [122, 120, 31],
                  [123, 120, 32],
                  [124, 121, 32],
                  [125, 121, 32],
                  [126, 121, 33],
                  [127, 122, 33],
                  [128, 122, 34],
                  [129, 122, 34],
                  [130, 123, 35],
                  [131, 123, 35],
                  [132, 123, 36],
                  [133, 124, 36],
                  [134, 124, 37],
                  [135, 124, 37],
                  [136, 125, 37],
                  [137, 125, 38],
                  [138, 125, 38],
                  [139, 126, 39],
                  [139, 126, 39],
                  [140, 126, 40],
                  [141, 126, 40],
                  [142, 127, 41],
                  [143, 127, 41],
                  [144, 127, 41],
                  [145, 128, 42],
                  [146, 128, 42],
                  [147, 128, 43],
                  [148, 129, 43],
                  [149, 129, 44],
                  [150, 129, 44],
                  [151, 130, 45],
                  [152, 130, 45],
                  [153, 130, 45],
                  [154, 131, 46],
                  [155, 131, 46],
                  [156, 131, 47],
                  [157, 132, 47],
                  [158, 132, 48],
                  [159, 132, 48],
                  [160, 133, 49],
                  [161, 133, 49],
                  [162, 133, 50],
                  [163, 134, 50],
                  [164, 134, 50],
                  [165, 134, 51],
                  [166, 135, 51],
                  [167, 135, 52],
                  [168, 135, 52],
                  [169, 136, 53],
                  [170, 136, 53],
                  [171, 136, 54],
                  [172, 137, 54],
                  [173, 137, 54],
                  [174, 137, 55],
                  [175, 138, 55],
                  [176, 138, 56],
                  [177, 138, 56],
                  [178, 139, 57],
                  [179, 139, 57],
                  [180, 139, 58],
                  [181, 140, 58],
                  [182, 140, 58],
                  [183, 140, 59],
                  [184, 141, 59],
                  [185, 142, 62],
                  [186, 144, 65],
                  [187, 146, 68],
                  [188, 147, 71],
                  [189, 149, 74],
                  [190, 151, 77],
                  [192, 153, 80],
                  [193, 155, 83],
                  [194, 156, 86],
                  [195, 158, 90],
                  [196, 160, 93],
                  [197, 162, 96],
                  [198, 164, 99],
                  [199, 165, 102],
                  [201, 167, 105],
                  [202, 169, 108],
                  [203, 171, 111],
                  [204, 173, 114],
                  [205, 174, 117],
                  [206, 176, 120],
                  [207, 178, 123],
                  [208, 180, 126],
                  [210, 182, 130],
                  [211, 184, 133],
                  [212, 185, 136],
                  [213, 187, 139],
                  [214, 189, 142],
                  [215, 191, 145],
                  [216, 193, 148],
                  [217, 194, 151],
                  [219, 196, 154],
                  [220, 198, 157],
                  [221, 200, 160],
                  [222, 202, 163],
                  [223, 203, 166],
                  [224, 205, 170],
                  [225, 207, 173],
                  [226, 209, 176],
                  [228, 211, 179],
                  [229, 212, 182],
                  [230, 214, 185],
                  [231, 216, 188],
                  [232, 218, 191],
                  [233, 220, 194],
                  [234, 221, 197],
                  [235, 223, 200],
                  [237, 225, 203],
                  [238, 227, 207],
                  [239, 229, 210],
                  [240, 230, 213],
                  [241, 232, 216],
                  [242, 234, 219],
                  [243, 236, 222],
                  [245, 238, 225],
                  [246, 240, 228],
                  [247, 241, 231],
                  [248, 243, 234],
                  [249, 245, 237],
                  [250, 247, 240],
                  [251, 249, 243],
                  [252, 250, 247],
                  [254, 252, 250],
                  [255, 254, 253],
                  [255, 255, 255]
                 ])

    cm = ListedColormap(C/255.)
    return cm

def terrain_cmap_50():
    """
     Custom terrain colormap with 50 distinct colors
    """
    C = np.array([[2, 97, 0],
                  [6, 98, 0],
                  [11, 98, 0],
                  [16, 99, 0],
                  [20, 100, 0],
                  [25, 101, 0],
                  [30, 102, 0],
                  [34, 103, 0],
                  [39, 104, 0],
                  [44, 105, 0],
                  [48, 106, 0],
                  [53, 107, 0],
                  [58, 108, 0],
                  [63, 109, 2],
                  [68, 110, 4],
                  [73, 111, 7],
                  [78, 112, 9],
                  [83, 113, 12],
                  [88, 114, 15],
                  [93, 115, 17],
                  [98, 116, 20],
                  [103, 116, 22],
                  [109, 117, 25],
                  [114, 118, 27],
                  [119, 119, 30],
                  [124, 121, 32],
                  [129, 122, 34],
                  [134, 124, 37],
                  [139, 126, 39],
                  [144, 127, 41],
                  [149, 129, 44],
                  [155, 131, 46],
                  [160, 133, 48],
                  [165, 134, 51],
                  [170, 136, 53],
                  [175, 138, 55],
                  [180, 139, 58],
                  [185, 143, 64],
                  [191, 152, 80],
                  [197, 162, 96],
                  [203, 171, 112],
                  [209, 181, 128],
                  [215, 190, 144],
                  [221, 199, 160],
                  [226, 209, 176],
                  [232, 218, 192],
                  [238, 228, 208],
                  [244, 237, 224],
                  [250, 246, 240],
                  [255, 255, 255]
                 ])

    cm = ListedColormap(C/255.)
    return cm

if __name__ == "__main__":

    #create some random terrain field
    rand_terrain = np.random.randint(100, 5001, (10, 10))

    plt.figure(1)
    plt.title('Terrain ColorMap with 256 colors')
    plt.imshow(rand_terrain, cmap=terrain_cmap_256())  # for example
    plt.colorbar()

    plt.figure(2)
    plt.title('Terrain ColorMap with 50 colors')
    plt.imshow(rand_terrain, cmap=terrain_cmap_50())  # for example
    plt.colorbar()

    plt.show()