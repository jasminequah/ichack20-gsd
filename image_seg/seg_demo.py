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
from tflite_segmentation import Segmentor, get_foreground, add_background, combine_foregrounds, vis_segmentation


segm = Segmentor()


def run_visualization(path):
    """Inferences DeepLab model and visualizes result."""
    original_im = Image.open(path)
    img_array = np.asarray(original_im.convert('RGB'))
    seg_map = segm.get_segment_map(img_array)
    out_image = get_foreground(original_im, seg_map)

    vis_segmentation([original_im], [seg_map], [out_image])


def run_visualization2(path1, path2):
    """Inferences DeepLab model and visualizes result."""
    img1 = Image.open(path1)
    img_array1 = np.asarray(img1.convert('RGB'))
    seg_map1 = segm.get_segment_map(img_array1)
    img2 = Image.open(path2)
    img_array2 = np.asarray(img2.convert('RGB'))
    seg_map2 = segm.get_segment_map(img_array2)
    out_image = combine_foregrounds(img1, seg_map1, img2, seg_map2)

    vis_segmentation([img1, img2], [seg_map1, seg_map2], [out_image])


# seg_maps = []
# imgs = []
# out_imgs = []
# for i in range(2,10):
#     # file = open("debug/seg" + str(i) + ".pkl", 'rb')
#     # seg_maps.append(pickle.load(file))
#     # file.close()
#     try:
#
#         file = open("debug/frame" + str(i) + ".pkl", 'rb')
#         imgs.append(pickle.load(file))
#         file.close()
#         file = open("debug/seg" + str(i) + ".pkl", 'rb')
#         seg_maps.append(pickle.load(file))
#         file.close()
#         # seg_maps.append(get_segment_map(imgs[-1]))
#         # out_imgs.append(get_foreground(imgs[-1], seg_maps[-1]))
#         file = open("debug/out" + str(i) + ".pkl", 'rb')
#         out_imgs.append(pickle.load(file))
#        file.close()
#     except:
#         pass
#
# vis_segmentation(imgs, seg_maps, out_imgs)

run_visualization('./zuck.jpeg')
# run_visualization2('./billgates.jpg', './billgates2.jpg')

# i = 0
# def segment(frame):
#     global seg_map1, seg_map2, use_first, i
#
#     seg_map = segm.get_segment_map(frame)
#
#     # file = open("debug/seg" + str(i) + ".pkl", 'wb')
#     # pickle.dump(seg_map, file)
#     # file.close()
#     # file = open("debug/frame" + str(i) + ".pkl", 'wb')
#     # pickle.dump(frame, file)
#     # file.close()
#     # i +=1
#
#     if use_first:
#         seg_map2 = seg_map
#     else:
#         seg_map1 = seg_map
#     use_first = not use_first
#
#
# cap = cv2.VideoCapture(0)
# ret, frame = cap.read()
#
# # Our operations on the frame come here
# seg_map1 = segm.get_segment_map(frame)
# seg_map2 = seg_map1.copy()
# use_first = True
#
# executor = ThreadPoolExecutor(2)
# future = executor.submit(segment, frame)
#
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#     if future.done():
#         future = executor.submit(segment, frame)
#
#     # # Our operations on the frame come here
#     # seg_map = get_segment_map(frame)
#     if use_first:
#         seg_map = seg_map1.copy()
#     else:
#         seg_map = seg_map2.copy()
#
#     # out_image = get_foreground(frame, seg_map)
#     rev_frame = frame[:,::-1]
#     rev_sm = seg_map[:,::-1]
#     foreground = combine_foregrounds(frame, seg_map, rev_frame, rev_sm)
#     out_image = add_background(frame, foreground, seg_map + rev_sm)
#
#     # Display the resulting frame
#     cv2.imshow('frame', out_image)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()
