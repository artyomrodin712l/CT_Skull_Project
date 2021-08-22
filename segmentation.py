import sys
import numpy as np
import skimage.io
import skimage.filters
import skimage.io as io
import matplotlib.pyplot as plt


path = "./images/IMG"
imgs_skulls = []

for i in range(256):
    image = io.imread(path + str(i) + ".png")
    imgs_skulls.append(image)


# Сегментация 
def filtering_image(image):
    sigma = 2
    blur = skimage.color.rgb2gray(image)
    blur = skimage.filters.gaussian(blur, sigma=sigma)

    t = skimage.filters.threshold_otsu(blur) * 3.2

    mask = blur > t

    selected_part = np.zeros_like(image)
    selected_part[mask] = image[mask]

    return selected_part

results = [filtering_image(image) for image in imgs_skulls]

#for i in range(0, 2):
#    io.imshow(results[i], cmap="gray")
#    io.show()

#for i in range(0, 256):
#    io.imsave(("./resultsFilter/resultFil" + str(i) + ".png"), results[i])

