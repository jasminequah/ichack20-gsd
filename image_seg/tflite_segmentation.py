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
urllib.request.urlretrieve('https://storage.googleapis.com/download.tensorflow.org/models/tflite/gpu/deeplabv3_257_mv_gpu.tflite', 'model.tflite')

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="./model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_details, output_details

# The function `get_tensor()` returns a copy of the tensor data.
# Use `tensor()` in order to get a pointer to the tensor.
output_data = interpreter.get_tensor(output_details[0]['index'])
print(output_data)

def vis_segmentation(image, labels, width, height):
  """Visualizes input image, segmentation map and overlay view."""
  plt.figure(figsize=(15, 5))
  grid_spec = gridspec.GridSpec(1, 4, width_ratios=[6, 6, 6, 1])

  plt.subplot(grid_spec[0])
  plt.imshow(image)
  plt.axis('off')
  plt.title('input image')

  seg_map = np.zeros((257,257))
  for i in range(257):
    for j in range(257):
      seg_map[i,j] = np.argmax(labels[i,j])
      # print(labels[i,j])

  print(seg_map.shape)
  seg_map = imresize(seg_map, (height, width))
  print(seg_map.shape)

  plt.subplot(grid_spec[1])
  plt.imshow(seg_map, cmap='hot', interpolation='nearest')
  plt.axis('off')
  plt.title('segmentation map ???')

  plt.subplot(grid_spec[2])
  out_image = np.asarray(image).copy()
  print('seg_map', seg_map.shape)
  print('out_image', out_image.shape)
  out_image[seg_map == 0] = 0
  plt.imshow(out_image)
  plt.axis('off')
  plt.title('foreground')

  plt.grid('off')
  plt.show()


def run_visualization(path):
  """Inferences DeepLab model and visualizes result."""
  original_im = Image.open(path)

  width, height = original_im.size
  target_size = (257, 257)
  resized_image = original_im.convert('RGB').resize(target_size, Image.ANTIALIAS)
  img_array = np.array([np.asarray(resized_image)], dtype=np.float32)
  img_mean = 128.0
  img_std = 128.0
  img_array = (img_array - img_mean) / img_std
  print(img_array.shape)

  img_tensor = tf.convert_to_tensor(img_array, np.float32)

  t1 = time.perf_counter()
  interpreter.set_tensor(input_details[0]['index'], img_tensor)
  interpreter.invoke()
  t2 = time.perf_counter()

  print(t2-t1, 'seconds')

  output_data = interpreter.get_tensor(output_details[0]['index'])
  print(output_data[0].shape)
  print(output_data[0,:,:,0])

  vis_segmentation(original_im, output_data[0], width, height)



run_visualization('./zuck.jpeg')
