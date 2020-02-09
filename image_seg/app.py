from flask import Flask, jsonify, request, render_template
from tflite_segmentation import get_foreground, Segmentor
import numpy as np
from flask_cors import CORS
import cv2
import pickle
import json

app = Flask(__name__)
CORS(app)
i = 0
@app.route('/segment', methods=['GET', 'POST'])
def segment_image():
    # @after_this_request
    # def add_header(response):
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    segm = Segmentor()

    # POST request
    if request.method == 'POST':
        # width = request.form.width
        # height = request.form.height
        data = request.form
        # print(data)
        # data = request.get_json()
        # print(type(data.to_dict()['file']))
        string = data.to_dict()['file']
        arr = np.fromstring(string, dtype=np.uint8, sep=',')


        # image = np.array(list(data.to_dict()['file']), dtype=int)
        # print(data)
        image = arr.reshape(300,400,4)
        # if (np.all(image == 0) or np.all(image == 255))):
        #     return {status: "500"}
        if np.all(image[:,:,:-1] == 0):
            return {'status': "500"}
        # print(arr[:10])
        rgb = image[:,:,:-1]

        global i
        file = open("debug/frame" + str(i) + ".pkl", 'wb')
        pickle.dump(rgb, file)
        file.close()

        # print(height)
        print("=============================================")
        seg_map = segm.get_segment_map(rgb.copy())
        # out_image = get_foreground(rgb, seg_map)
        # print(rgb)

        # image[:,:,:-1] = out_image

        # file = open("debug/seg" + str(i) + ".pkl", 'wb')
        # pickle.dump(seg_map, file)
        # file.close()
        # file = open("debug/out" + str(i) + ".pkl", 'wb')
        # pickle.dump(out_image, file)
        # file.close()
        # i +=1

        # out_stream = image.flatten()

        seg_stream = seg_map.flatten()

        # return {'file': json.dumps(out_stream.tolist())}
        return {'file': json.dumps(seg_stream.tolist())}


    # GET request
    else:
        return request.query_string
        # message = {'greeting':'Hello from Flask!'}
        # return jsonify(message)  # serialize and use JSON headers

@app.route('/test')
def test_page():
    # look inside `templates` and serve `index.html`
    return render_template('index.html')
