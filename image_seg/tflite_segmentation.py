import os
import urllib.request
import numpy as np
import tensorflow as tf
import time
from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from io import BytesIO
from scipy.misc import imresize
import cv2
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import pickle

class Segmentor(object):

    def __init__(self):
        # To download the model
        # urllib.request.urlretrieve('https://storage.googleapis.com/download.tensorflow.org/models/tflite/gpu/deeplabv3_257_mv_gpu.tflite', 'model.tflite')

        # Load TFLite model and allocate tensors.
        self.interpreter = tf.lite.Interpreter(model_path="./model.tflite")
        self.interpreter.allocate_tensors()


    def get_segment_map(self, img_array):
        height, width, _ = img_array.shape
        img_array = imresize(img_array, (257, 257))
        img_array = np.array([img_array], dtype=np.float32)
        img_array = (img_array - 128.0) / 128.0
        img_tensor = tf.convert_to_tensor(img_array, np.float32)

        # Get input and output tensors.
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # t1 = time.perf_counter()
        self.interpreter.set_tensor(input_details[0]['index'], img_tensor)
        self.interpreter.invoke()
        # t2 = time.perf_counter()
        # print('segmentation took', t2-t1, 'seconds')

        output_data = self.interpreter.get_tensor(output_details[0]['index'])
        seg_map = np.zeros((257,257))
        for i in range(257):
            for j in range(257):
                seg_map[i,j] = np.argmax(output_data[0,i,j])

        # values, counts = np.unique(seg_map, return_counts=True)
        # if (len(counts) == 1 or np.max(counts[1:]) < 3000) and default is not None:
        #     return default

        seg_map[seg_map != 15] = 0
        seg_map = np.array(imresize(seg_map, (height, width))/255, dtype = int)

        return seg_map



def get_foreground(image, seg_map):
    out_image = np.asarray(image).copy()
    out_image[seg_map == 0] = 0
    return out_image


def combine_foregrounds(image1, seg_map1, image2, seg_map2):
    foreground1 = get_foreground(image1, seg_map1)
    seg_map_diff = seg_map2.copy()
    seg_map_diff[seg_map1 != 0] = 0
    foreground2_diff = get_foreground(image2, seg_map_diff)
    out_image = foreground1 + foreground2_diff
    return out_image


def add_background(image, foreground, seg_map):
    out_image = image.copy()
    out_image[seg_map != 0] = foreground[seg_map != 0]
    return out_image


def vis_segmentation(images, seg_maps, out_images):
    """Visualizes input image, segmentation map and overlay view."""
    plt.figure(figsize=(10, 7))
    grid_spec = gridspec.GridSpec(3, len(images))

    for i in range(len(images)):
        plt.subplot(grid_spec[0, i])
        plt.imshow(images[i])
        plt.axis('off')
        plt.title('input image {0}'.format(i))


    for i in range(len(images)):
        plt.subplot(grid_spec[1, i])
        plt.imshow(seg_maps[i], cmap='hot', interpolation='nearest')
        plt.axis('off')
        plt.title('segmentation map {0}'.format(i))

    for i in range(len(out_images)):
        plt.subplot(grid_spec[2, i])
        plt.imshow(out_images[i])
        plt.axis('off')
        plt.title('result')

    plt.grid('off')
    plt.show()
