from numpy.core.records import array
from reconstruction import plot_3d
from segmentation import filtering_image
import PySimpleGUI as sg
import sys
import os.path
import PIL.Image
import io
import base64
import skimage.io
import skimage.filters
import skimage.io as bio
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.image as img
import cv2
import pickle
import numpy
from stl import mesh
import surf2stl
from mpl_toolkits import mplot3d

def convert_to_bytes(file_or_bytes, resize=None):
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

sg.theme('Blue Mono') # тема интерфейса

left_col = [[sg.Text('Importing a folder with images:')],
            [sg.In(size=(25,1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Listbox(values=[], enable_events=True, size=(32,20),key='-FILE LIST-')],
            [sg.Text('Resize to'), sg.In(key='-W-', size=(5,1)), sg.In(key='-H-', size=(5,1))]]

images_col = [[sg.Text('You choose from the list:')],
              [sg.Text(size=(40,1), key='-TOUT-')],
              [sg.Image(key='-IMAGE-')]]

# ?????????????

#images = [[sg.Text('You choose from the list:')],
#             [sg.Text(size=(40,1), key='-TOUT-')],
 #             [sg.Image(key='-IMAGE1-')]]

segment_image = [[sg.Button('SEGMENT')],
                 [sg.Text('ПРОСМОТР изображений после сегментации:')],
                 #[sg.Text(size=(40, 1), key='-TOUT1-')],
#                 [sg.Image(key='-IMAGE1-')],
                 [sg.Text('Save segmented images to folder:')],
                 [sg.In(size=(25,1), enable_events=True, key='-FOLDER1-'), sg.SaveAs()]]

# ??????????????
layout_reconstruct = [[sg.Button('Reconstruct skull')],
                      [sg.Text('График с реконструкцией черепа (кубы)')]]

layout = [[sg.Column(left_col, element_justification='c'), sg.VSeperator(),
           sg.Column(images_col, element_justification='c'), sg.VSeperator(),
           sg.Column(segment_image, element_justification='c'),  sg.VSeperator(),
           sg.Column(layout_reconstruct, element_justification='c')]]


# , no_titlebar=True, alpha_channel=.5, grab_anywhere=True -для прозрачности
window = sg.Window('3D Reconstruction', layout, resizable=True)

while True:
    event, values = window.read()
    if event in (None, 'Exit', 'Cancel'):
        break
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-FOLDER-':                         # Folder name was filled in, make a list of files in the folder
        folder = values['-FOLDER-']
        try:
            file_list = os.listdir(folder)         # get list of files in folder
        except:
            file_list = []
        fnames = [f for f in file_list if os.path.isfile(
            os.path.join(folder, f)) and f.lower().endswith((".png", ".jpg", "jpeg", ".tiff", ".bmp"))]
        window['-FILE LIST-'].update(fnames)
    elif event == '-FILE LIST-':    # A file was chosen from the listbox
        try:
            filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
            window['-TOUT-'].update(filename)
            if values['-W-'] and values['-H-']:
                new_size = int(values['-W-']), int(values['-H-'])
            else:
                new_size = None
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=new_size))
        except Exception as E:
            print(f'** Error {E} **')
            pass        # something weird happened making the full filename
    if event == 'SEGMENT':    # A file was chosen from the listbox
        filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
        folder = values['-FOLDER-']
#        img = bio.imread(folder + "/IMG1" + ".png")
        imgs_skulls = []
        image = cv2.imread(filename, 0)
        results = filtering_image(image)
        imgs_skulls.append(image)
        print(results)
        cv2.imshow('image', results)
    if event == 'Reconstruct skull':    # A file was chosen from the listbox
        filename = os.path.join(values['-FOLDER-'], values['-FILE LIST-'][0])
        image = cv2.imread(filename)
    #    axes = mplot3d.Axes3D(image)
        s = plot_3d(image)
#        VERTICE_COUNT = 100
#        data = numpy.zeros(image, dtype=mesh.Mesh.dtype)
#        your_mesh = mesh.Mesh(data, remove_empty_areas=False)
#       your_mesh.normals
#        your_mesh.v0, your_mesh.v1, your_mesh.v2
#        your_mesh.save('scull.stl')
        data = np.zeros(len(image), dtype=mesh.Mesh.dtype)
        mobius_mesh = mesh.Mesh(data, remove_empty_areas=False)
        mobius_mesh.save('mysurface.stl')

        plt.show()
# --------------------------------- Close & Exit ---------------------------------
window.close()