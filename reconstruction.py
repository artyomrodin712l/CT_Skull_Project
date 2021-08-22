from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure

# Сжатие изображений
# Сжимать изображение 100 на 100. а потом маршерующие кубы
def scale_image(input_image_path,
                output_image_path,
                width=100,
                height=100
                ):
    original_image = Image.open(input_image_path)
    w, h = original_image.size
    print('The original image size is {wide} wide x {height} '
          'high'.format(wide=w, height=h))

    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        # No width or height specified
        raise RuntimeError('Width or height required!')

    original_image.thumbnail(max_size, Image.ANTIALIAS)
    original_image.save(output_image_path)

    scaled_image = Image.open(output_image_path)
    width, height = scaled_image.size


# Сохранение изображений
#for i in range(256):
    #scale_image(input_image_path="./resultsFilter/resultFil" + str(i) + ".png",
     #           output_image_path="./resFilterScaling/resultFilSc" + str(i) + ".png")


path = "./resFilterScaling/resultFilSc"

def read_result_images(path):
    imgs_skulls = []
    for i in range(256):
        skull= cv2.imread(path + str(i) + ".png", cv2.IMREAD_GRAYSCALE)
        imgs_skulls.append(skull)
    return np.array(imgs_skulls)

# 3д реконструкция с помощью маршерующих кубов
def plot_3d(imgs):
    verts, faces, _, _ = measure.marching_cubes(imgs)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    mesh = Poly3DCollection(verts[faces])
    ax.add_collection3d(mesh)

    ax.set_xlim(0, imgs.shape[0])
    ax.set_ylim(0, imgs.shape[1])
    ax.set_zlim(0, imgs.shape[2])

imgs = read_result_images(path)

plot_3d(imgs)