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

# To download the model
# urllib.request.urlretrieve('https://storage.googleapis.com/download.tensorflow.org/models/tflite/gpu/deeplabv3_257_mv_gpu.tflite', 'model.tflite')

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="./model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


def get_segment_map(img_array):
    height, width, _ = img_array.shape
    img_array = imresize(img_array, (257, 257))
    img_array = np.array([img_array], dtype=np.float32)
    img_array = (img_array - 128.0) / 128.0
    img_tensor = tf.convert_to_tensor(img_array, np.float32)

    # t1 = time.perf_counter()
    interpreter.set_tensor(input_details[0]['index'], img_tensor)
    interpreter.invoke()
    # t2 = time.perf_counter()
    # print('segmentation took', t2-t1, 'seconds')

    output_data = interpreter.get_tensor(output_details[0]['index'])
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


def vis_segmentation(images, seg_maps, out_images):
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

    for i in range(len(out_images)):
        plt.subplot(grid_spec[2, i])
        plt.imshow(out_images[i])
        plt.axis('off')
        plt.title('result')

    plt.grid('off')
    plt.show()


def run_visualization(path):
    """Inferences DeepLab model and visualizes result."""
    original_im = Image.open(path)
    img_array = np.asarray(original_im.convert('RGB'))
    seg_map = get_segment_map(img_array)
    out_image = get_foreground(original_im, seg_map)

    vis_segmentation([original_im], [seg_map], [out_image])


def run_visualization2(path1, path2):
    """Inferences DeepLab model and visualizes result."""
    img1 = Image.open(path1)
    img_array1 = np.asarray(img1.convert('RGB'))
    seg_map1 = get_segment_map(img_array1)
    img2 = Image.open(path2)
    img_array2 = np.asarray(img2.convert('RGB'))
    seg_map2 = get_segment_map(img_array2)
    out_image = combine_foregrounds(img1, seg_map1, img2, seg_map2)

    vis_segmentation([img1, img2], [seg_map1, seg_map2], [out_image])


# seg_maps = []
# imgs = []
# out_imgs = []
# for i in range(3,10):
#     # file = open("debug/seg" + str(i) + ".pkl", 'rb')
#     # seg_maps.append(pickle.load(file))
#     # file.close()
#     file = open("debug/frame" + str(i) + ".pkl", 'rb')
#     imgs.append(pickle.load(file))
#     file.close()
#     seg_maps.append(get_segment_map(imgs[-1]))
#     out_imgs.append(get_foreground(imgs[-1], seg_maps[-1]))
#
# vis_segmentation(imgs, seg_maps, out_imgs)

# run_visualization('./billgates.jpg')
# run_visualization2('./billgates.jpg', './billgates2.jpg')

# i = 0
def segment(frame):
    global seg_map1, seg_map2, use_first, i

    seg_map = get_segment_map(frame)

    # file = open("debug/seg" + str(i) + ".pkl", 'wb')
    # pickle.dump(seg_map, file)
    # file.close()
    # file = open("debug/frame" + str(i) + ".pkl", 'wb')
    # pickle.dump(frame, file)
    # file.close()
    # i +=1

    if use_first:
        seg_map2 = seg_map
    else:
        seg_map1 = seg_map
    use_first = not use_first


cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Our operations on the frame come here
seg_map1 = get_segment_map(frame)
seg_map2 = seg_map1.copy()
use_first = True

executor = ThreadPoolExecutor(2)
future = executor.submit(segment, frame)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if future.done():
        future = executor.submit(segment, frame)

    # # Our operations on the frame come here
    # seg_map = get_segment_map(frame)
    if use_first:
        seg_map = seg_map1.copy()
    else:
        seg_map = seg_map2.copy()

    # out_image = get_foreground(frame, seg_map)
    rev_frame = frame[:,::-1]
    rev_sm = seg_map[:,::-1]
    out_image = combine_foregrounds(frame, seg_map, rev_frame, rev_sm)

    # Display the resulting frame
    cv2.imshow('frame', out_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
