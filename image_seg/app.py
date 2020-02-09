from flask import Flask, jsonify, request, render_template
from tflite_segmentation import get_foreground, Segmentor
import numpy as np

app = Flask(__name__)

segm = Segmentor()

@app.route('/segment', methods=['GET', 'POST'])
def segment_image():
    # @after_this_request
    # def add_header(response):
    #     response.headers['Access-Control-Allow-Origin'] = '*'

    # POST request
    if request.method == 'POST':
        # width = request.form.width
        # height = request.form.height
        data = request.form
        print(data)
        # data = request.get_json()
        # print(data)
        # image = np.array(data.to_dict(), dtype=int)
        # print(data)
        image = data.reshape(300,400,4)
        # print(height)
        print("=============================================")
        seg_map = segm.get_segment_map(image)
        out_image = segm.get_foreground(image, seg_map)
        print(image)
        # print(request.get_json())  # parse as JSON
        return 200, 'OK'

    # GET request
    else:
        return request.query_string
        # message = {'greeting':'Hello from Flask!'}
        # return jsonify(message)  # serialize and use JSON headers

@app.route('/test')
def test_page():
    # look inside `templates` and serve `index.html`
    return render_template('index.html')
