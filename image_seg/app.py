from flask import Flask, jsonify, request, render_template
from tflite_segmentation import get_foreground, Segmentor
import numpy as np
from flask_cors import CORS
import cv2
import pickle
import json

app = Flask(__name__)
CORS(app)

@app.route('/segment', methods=['GET', 'POST'])
def segment_image():
    segm = Segmentor()

    # POST request
    if request.method == 'POST':
        data = request.form

        string = data.to_dict()['file']
        arr = np.fromstring(string, dtype=np.uint8, sep=',')

        image = arr.reshape(300,400,4)
        if np.all(image[:,:,:-1] == 0):
            return {'status': "500"}
        rgb = image[:,:,:-1]

        seg_map = segm.get_segment_map(rgb.copy())
        seg_stream = seg_map.flatten()

        return {'file': json.dumps(seg_stream.tolist())}

    # GET request
    else:
        return request.query_string

@app.route('/test')
def test_page():
    # look inside `templates` and serve `index.html`
    return render_template('index.html')
