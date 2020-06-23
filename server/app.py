import uuid
import os
from flask import Flask, jsonify, request, flash, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile
import torch
from utils.dataset import FromFolder
from utils.inference import process_dataset
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

UPLOAD_FOLDER = '/home/test/Desktop/flask-vue-crud/client/src/assets/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


BOOKS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'read': True
    }
]

# IQ_SCORE=[
#     {
#         'id':1,
#         'score':1.23
#     },
#     {
#         'id':2,
#         'score':6.32
#     },
# ]

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


def remove_book(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            BOOKS.remove(book)
            return True
    return False


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book added!'
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)


@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file',
#                                     filename=filename))
#     return 

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)

@app.route('/result',methods=['GET'])
def result():
    return "File Uploaded Successfully"

#Upload
@app.route('/api/upload',methods=['GET','POST'])
def uploadFile():
    if request.method == 'POST':

        file = request.files['file']
        filename = secure_filename(file.filename)

        # Gen GUUID File Name
        # fileExt = filename.split('.')[1]
        # autoGenFileName = uuid.uuid4()

        # newFileName = str(autoGenFileName) + '.' + fileExt

        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'images/'))
        # for root, dirs, files in os.walk(os.path.join(app.config['UPLOAD_FOLDER'], 'images/')):
        #     for file in files:
        #         path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/'), file)
        #         os.remove(path)
                
        with zipfile.ZipFile(path, 'r') as zip_ref:
            # print(os.path.join(app.config['UPLOAD_FOLDER'], str(autoGenFileName),'/'))
            zip_ref.extractall(os.path.join(app.config['UPLOAD_FOLDER'], 'images/'))

        #Save file Info into DB
        # file = UploadFiles(fileName=newFileName, createdon=datetime.datetime.now(datetime.timezone.utc))

        # db.session.add(file)
        # db.session.commit()


        return redirect(url_for('result'))
        
#Upload
@app.route('/analysis',methods=['GET','POST'])
def analyzeFile():
    # response_object = {}
    if request.method == 'GET':
        print("xixi")
        IQ_SCORE = frames2Score()
        # response_object['score'] = IQ_SCORE
        print(IQ_SCORE)
        return jsonify(IQ_SCORE)
        # print(IQ_SCORE)
        # return IQ_SCORE

def frames2Score():
    trace_path = "models/model_video.pt"
    device = "cuda"
    frame_dir = UPLOAD_FOLDER+"images/"
    frames = os.listdir(frame_dir)
    model = torch.jit.load(trace_path, map_location=device)
    results = []
    for frame in frames:
        if frame=='icon.png':
            continue
        model.eval()
        model.requires_grad = False
        images_folder = Path(frame_dir+frame)
        dataset = FromFolder(folder=images_folder)
        result = process_dataset(model=model, dataset=dataset, batch_size=1,
                                num_workers=1, device=device,
                                output_key=1,
                                method="forward",  # method="forward" for metis_ops_current
                                )
        # print(results)
        # ret = []
        # for index, row in results.iterrows():
        #     el = {}
        #     el['id'] = int(index)
        #     el['frame'] = str(row['full_path'])
        #     el['score'] = float(row['predicted'])
        #     ret.append(el)
        # # json_ret['data'] = results
        # print(ret)
        # return {'ret': ret, 'col':['id','frame','score']}
        # return results
        results.append(result)
    return results
        # results.to_csv(frame+".csv")

if __name__ == '__main__':
    app.run(host= '0.0.0.0')