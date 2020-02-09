from flask import Flask, jsonify, request, render_template
from tflite_segmentation import get_foreground, Segmentor
import numpy as np

app = Flask(__name__)


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
        print(type(data.to_dict()['file']))
        string = data.to_dict()['file']
        arr = np.fromstring(string, dtype=int, sep=',')
        print(arr[:10])
        # image = np.array(list(data.to_dict()['file']), dtype=int)
        # print(data)
        image = arr.reshape(300,400,4)
        rgb = image[:,:,:-1]
        # print(height)
        print("=============================================")
        seg_map = segm.get_segment_map(rgb.copy())
        out_image = get_foreground(rgb, seg_map)
        print(rgb)

        image[:,:,:-1] = out_image

        out_stream = out_image.flatten()

        return {'file':np.array2string(out_stream, separator=",")[1:-1]}

    # GET request
    else:
        return request.query_string
        # message = {'greeting':'Hello from Flask!'}
        # return jsonify(message)  # serialize and use JSON headers

@app.route('/test')
def test_page():
    # look inside `templates` and serve `index.html`
    return render_template('index.html')
