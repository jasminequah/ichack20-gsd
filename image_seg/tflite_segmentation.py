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

# To download the model
# urllib.request.urlretrieve('https://storage.googleapis.com/download.tensorflow.org/models/tflite/gpu/deeplabv3_257_mv_gpu.tflite', 'model.tflite')

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="./model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


def get_segment_map(image):
    width, height = image.size
    resized_image = image.convert('RGB').resize((257, 257), Image.ANTIALIAS)
    img_array = np.array([np.asarray(resized_image)], dtype=np.float32)
    img_array = (img_array - 128.0) / 128.0
    img_tensor = tf.convert_to_tensor(img_array, np.float32)

    t1 = time.perf_counter()
    interpreter.set_tensor(input_details[0]['index'], img_tensor)
    interpreter.invoke()
    t2 = time.perf_counter()
    print('segmentation took', t2-t1, 'seconds')

    output_data = interpreter.get_tensor(output_details[0]['index'])
    seg_map = np.zeros((257,257))
    for i in range(257):
        for j in range(257):
            seg_map[i,j] = np.argmax(output_data[0,i,j])
    seg_map = imresize(seg_map, (height, width))

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


def vis_segmentation(images, seg_maps, out_image):
    """Visualizes input image, segmentation map and overlay view."""
    plt.figure(figsize=(15, 10))
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

    plt.subplot(grid_spec[2, 0])
    plt.imshow(out_image)
    plt.axis('off')
    plt.title('result')

    plt.grid('off')
    plt.show()


def run_visualization(path):
    """Inferences DeepLab model and visualizes result."""
    original_im = Image.open(path)
    seg_map = get_segment_map(original_im)
    out_image = get_foreground(original_im, seg_map)

    vis_segmentation([original_im], [seg_map], out_image)


def run_visualization2(path1, path2):
    """Inferences DeepLab model and visualizes result."""
    img1 = Image.open(path1)
    seg_map1 = get_segment_map(img1)
    img2 = Image.open(path2)
    seg_map2 = get_segment_map(img2)
    out_image = combine_foregrounds(img1, seg_map1, img2, seg_map2)

    vis_segmentation([img1, img2], [seg_map1, seg_map2], out_image)


# run_visualization('./billgates.jpg')
run_visualization2('./billgates.jpg', './billgates2.jpg')
