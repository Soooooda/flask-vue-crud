import uuid
import os
from flask import Flask, jsonify, request, session, flash, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import zipfile
import torch
from utils.dataset import FromFolder
from utils.inference import process_dataset
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from torchvision import transforms
import csv
import cv2
from matplotlib.colors import LinearSegmentedColormap
import redis
from flask_session import Session
from glob import glob
import json

UPLOAD_FOLDER = '/home/test/Desktop/flask-vue-crud/assets/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
   

PWD = '123456'
USERNAME = 'test'
f_session = Session()

stats = []

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# the redis part didn't work
app.config['SECRET_KEY'] = 'wozaiperflabdagong2'
app.config['SESSION_USE_SIGNER'] = True  # 是否对发送到浏览器上session的cookie值进行加密
app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
app.config['SESSION_KEY_PREFIX'] = 'session:'  # 保存到session中的值的前缀
app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 失效时间 秒
app.config['SESSION_REDIS'] = redis.Redis.from_url("redis://0.0.0.0:6379")  # redis数据库连接

# 绑定flask 对象
f_session.init_app(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
# cors = CORS(app, origins=["*"], headers=['Content-Type'], expose_headers=['Access-Control-Allow-Origin'], supports_credentials=True)

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


# Load the videos
VIDEOS = []
Video_arr = []
Video_dir = UPLOAD_FOLDER
# Video_arr = os.listdir(Video_dir)
# print(Video_arr)
print('hi')

types = ('*.mp4', '*.mkv') # the tuple of file types
for files in types:
    Video_arr.extend(glob(os.path.join(Video_dir,'videos/'+ files)))

for v in Video_arr:
    v = v.split('/')[-1].split('.')[0]
    print(v)
    vi = {}
    vi['id'] = uuid.uuid4().hex
    vi['title'] = v
    # vi['author'] = 'anony'
    vi['read'] = False
    if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'],'frames/'+ v)):
        vi['read'] = True
    VIDEOS.append(vi)

#@app.after_request
# def add_header(response):
#     response.headers['X-Content-Type-Options'] = 'nosniff'
#     return response

# 0 成功
# -1 用户名或密码错误
@app.route('/login', methods=['GET', 'POST'])
def login():
    # session['test10111'] = 'useredis2223'
    response_object = {'status': '-1'}
    if request.method == 'POST':
        post_data = request.get_json()
        userName = post_data.get('username')
        pwd = post_data.get('password')
        print(userName,pwd)
        if userName == USERNAME and pwd == PWD:
            print('yes!')
            response_object['status'] = '0'
            session['status'] = '0'
        else:
            session['status'] = '-1'
    else:
        # print(session['status'])
        if 'status' in session and session['status'] == '0':
            print('here is session')
            response_object['status'] = '0'
        else:
            response_object['status'] = '-1'
    print('here')
    # response = make_response(jsonify(response=get_articles(ARTICLES_NAME)))
    return jsonify(response_object)# , 200, {'Access-Control-Allow-Credentials': 'true','Access-Control-Allow-Origin':'http://10.19.199.137:5000'}



@app.route('/getsession', methods=['GET', 'POST'])
def getsession():
    response_object = {'status': session['test10111']}
    # if request.method == 'GET':
    #     response_object['status'] = session.get('status')
    return jsonify(response_object)

def remove_book(book_id):
    for book in VIDEOS:
        if book['id'] == book_id:
            print("remove")
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+book['title']+'.mp4')):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+book['title']+'.mp4'))
            if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], 'frames/'+book['title'])):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'frames/'+book['title']))
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+book['title']+'.json')):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+book['title']+'.json'))
            VIDEOS.remove(book)
            print(VIDEOS)
            return True
    return False

@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        print('put success')
        print(book_id)
        post_data = request.get_json()
        

        # process video
        # print(post_data.get('read'))

        readOrNot = True
        for book in VIDEOS:
            if book['id'] == book_id:
                if book['read']==True:
                    readOrNot = False
                book['read'] = readOrNot

        if readOrNot==True:
            if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], 'frames/'+post_data.get('title')))!=True:
                path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+post_data.get('title')+'.mp4')
                print("read data video")
                print(path)
                vidcap = cv2.VideoCapture(path)
                success2,image2 = vidcap.read()
                count = 0
                print('Read a new video: ', success2)
                os.system('mkdir /home/test/Desktop/flask-vue-crud/assets/frames/'+post_data.get('title'))
                while success2:
                    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], "frames/"+post_data.get('title')+"/frame%d.png" % count), image2)
                    success2,image2 = vidcap.read()
                    count += 1
            # turn frames into JSONs
            if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+post_data.get('title')+'.json'))!=True:
                frames2Score(post_data.get('title'))

        else:
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+post_data.get('title')+'.json')):
                os.system("rm " + os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+post_data.get('title')+'.json'))

        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)

@app.route('/result',methods=['GET'])
def result():
    print ("test")
    return "File Uploaded Successfully"

#Upload Video
@app.route('/upload/video',methods=['GET','POST'])
def uploadVideo():
    print("hehe")
    if request.method == 'POST':
        print(request)
        # print(request.files)
        file = request.files['file']
        print('file')
        filename = secure_filename(file.filename)


        path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+filename)
        print('begin save')
        file.save(path)
        print('remove former directories')

        # os.system("mkdir " + os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+filename.split('.')[0]))
        # print('create path'+filename.split('.')[0])
        # print('finish')
        # for root, dirs, files in os.walk(os.path.join(app.config['UPLOAD_FOLDER'], 'images/')):
        #     for file in files:
        #         path = os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/'), file)
        #         os.remove(path)

        # # process video
        # vidcap = cv2.VideoCapture(path)
        # success,image = vidcap.read()
        # count = 0
        # print('Read a new video: ', success)
        # while success:
        #     cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+filename.split('.')[0])+"/frame%d.png" % count, image)     # save frame as JPEG file      
        #     success,image = vidcap.read()
        #     count += 1


               
        # with zipfile.ZipFile(path, 'r') as zip_ref:
            # print(os.path.join(app.config['UPLOAD_FOLDER'], str(autoGenFileName),'/'))
            # zip_ref.extractall(os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'))

        #Save file Info into DB
        # file = UploadFiles(fileName=newFileName, createdon=datetime.datetime.now(datetime.timezone.utc))
        # db.session.add(file)
        # db.session.commit()
        return jsonify({'status':filename.split('.')[0]})




#Upload Scenes
@app.route('/upload/scene',methods=['GET','POST'])
def uploadScene():
    if request.method == 'POST':
        path = os.path.join(app.config['UPLOAD_FOLDER'], 'images/')
        print(request)
        f = request.files['file']
        print(f.filename)
        f.save(path+f.filename)
        iq = image2Score(f.filename)
        path = f.filename.split('.')[0] + '_result.png'
        # image_file.save(path)
        return jsonify({'iq':str(iq), 'path':path})# 'http://10.19.199.137/'+ path
        
#Analyze Videos
@app.route('/analysis',methods=['GET','POST'])
def analyzeFile():
    # response_object = {}
    if request.method == 'GET':
        print("xixi")
        # IQ_SCORE = frames2Score()
        IQ_SCORE = []
        json_path = os.listdir('/home/test/Desktop/flask-vue-crud/assets/json/')
        for j in json_path:
            f = open('/home/test/Desktop/flask-vue-crud/assets/json/'+j)
            json_string= json.load(f)
            IQ_SCORE.append(json_string)
            f.close()

        # response_object['score'] = IQ_SCORE
        # print(IQ_SCORE)
        return jsonify(IQ_SCORE)
        # print(IQ_SCORE)
        # return IQ_SCORE

def frames2Score(frame):
    trace_path = "models/model_dlss.pt"
    device = "cuda"
    frame_dir = '/home/test/Desktop/flask-vue-crud/assets/frames/'+frame
    result_dir = '/home/test/Desktop/flask-vue-crud/assets/json/'+frame+'.json'
    # os.system('touch '+ result_dir)
    # frames = os.listdir(frame_dir)
    model = torch.jit.load(trace_path, map_location=device)
    # results = []
    # for frame in frames:
        # if frame=='icon.png':
            # continue
    model.eval()
    model.requires_grad = False
    images_folder = Path(frame_dir)
    dataset = FromFolder(folder=images_folder)
    result = process_dataset(model=model, dataset=dataset, batch_size=1,
                            num_workers=2, device=device,
                            output_key=1,
                            method="dense_prediction",  # method="forward" for metis_ops_current
                            )
        # results.append(result)
    print(result)
    print(type(result))
    with open(result_dir, 'w') as f:
        json.dump(result, f)
    return result


DEFAULT_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # imagenet normalization
])

def display_prediction(img_orig, score):
    img = img_orig.copy()
    # score = float(score)
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # color = (255, 255, 255)
    # img[:100, 0:250, :] = 0
    # cv2.putText(img, f"{score:.1f}", (20, 70), font, 2, color, 10, cv2.LINE_AA)
    return img

def predict_on_image(model, method, img, transform, device):
    processed_img = transform(img).unsqueeze(0).to(device)
    
    if method is not None:
        output = getattr(model, method)(processed_img)
    else:
        output = model(processed_img)
    
    heatmap_raw, score = output
    return heatmap_raw.cpu().detach().numpy(), score.cpu().detach().item()

def full_predict(image_path, model, method, heatmap_params, res_folder, device, transform=DEFAULT_TRANSFORM):
    image = cv2.cvtColor(cv2.imread(str(image_path)), cv2.COLOR_BGR2RGB)
    hm_raw, score = predict_on_image(model=model, method=method, img=image, transform=transform, device=device)
    
    heatmap = generate_heatmap(dense_prediction=hm_raw, image=image,
                              vmin=heatmap_params.vmin, vmax=heatmap_params.vmax,
                              alpha=heatmap_params.alpha, adapt_transperancy=heatmap_params.adapt_transperancy)
    
    heatmap_with_score = display_prediction(heatmap, score)
    # orig_with_score = display_prediction(image, score)
    print(os.path.join(app.config['UPLOAD_FOLDER'], 'heatmaps/')+image_path.split('.')[0]+"_result.png")
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'heatmaps/')+image_path.split('/')[-1].split('.')[0]+"_result.png", heatmap_with_score[..., ::-1])

    
    # for name, img in zip(["orig_score", "heatmap"],
    #                      [orig_with_score, heatmap_with_score]):
    #     filename = f"{name}_{image_path.stem}_{score:.2f}.jpg"
    #     cv2.imwrite(str(res_folder / filename), img[..., ::-1])
        
    return score

from collections import namedtuple
HeatmapParams = namedtuple("HeatmapParams", 
                          ["vmin", "vmax", "alpha", "adapt_transperancy"])
params_mapping = {"model_dlss": 
                      HeatmapParams(vmin=0, vmax=10.0, alpha=0.5, adapt_transperancy=False),
                 "metis_ops_current": 
                      HeatmapParams(vmin=-20, vmax=20.0, alpha=0.5, adapt_transperancy=False)}
methods_mapping = {"model_dlss": "dense_prediction",
                   "metis_ops_current": "forward",
                  }


def image2Score(path):
    trace_path = "models/model_dlss.pt"#models/model.pt
    model_name = Path(trace_path).parts[-1].split('.')[0]
    method = methods_mapping[model_name]
    model = torch.jit.load(trace_path)#, map_location="cuda"
    model.eval()
    model.requires_grad = False

    # data_transform = transforms.Compose([
    #     transforms.ToTensor(),
    #     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # imagenet normalization
    # ])
    
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'images/')+path
    device = "cuda"

    iq = full_predict(image_path=image, model=model, method=method, 
                     heatmap_params=params_mapping[model_name],
                     res_folder="", device=device)
    # tensor = data_transform(image).unsqueeze(0).to("cpu")
    # output = getattr(model, method)(tensor)#model(tensor)
    # iq_scores_heatmap, iq_score = output
    # iq_scores_heatmap = iq_scores_heatmap.cpu().detach().numpy()
    # iq_score = iq_score.cpu().detach().item()
    # heatmap = generate_heatmap(dense_prediction=iq_scores_heatmap,#.detach().numpy(),
    #                                image=image, adapt_transperancy=False)
    # cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'heatmaps/')+path.split('.')[0]+"_result.png", heatmap[..., ::-1])
    # iq = iq_score.detach().numpy()[0]
    # print("iq score: %f"%(iq))
    return iq

def generate_heatmap(dense_prediction: np.ndarray, image: np.ndarray, alpha: float = 0.3, vmin: float = 0.0,
                    vmax: float = 10.0,
                    adapt_transperancy: bool = True):
    """
    Use the provided dense_prediction to generate a heatmap.

    :param dense_prediction: the dense prediction output of the model
    :param image: the image to draw the heatmap onto
    :param vmin: minimal expected prediction (used for color normalization)
    :param vmax: maximum expected prediction (used for color normalization)
    :param alpha: heatmap transparency (0 -- see only image, 1 -- only heatmap)
    :param adapt_transperancy: scale transparency linearly so that values in the middle are transparent

    :return: resulted heatmap

    """
    dense_prediction = np.squeeze(dense_prediction)

    cmap = LinearSegmentedColormap.from_list('name', ['red', 'green'])
    norm = plt.Normalize(vmin, vmax, clip=True)

    prediction_norm = norm(dense_prediction)
    prediction_int = np.array(cmap(prediction_norm) * 255, dtype=np.uint8)[:, :, [0, 1, 2]]
    prediction_int = cv2.resize(prediction_int, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LINEAR)

    if adapt_transperancy:
        blend = np.abs(prediction_norm - 0.5) * 2 * alpha
    else:
        blend = np.ones_like(prediction_norm) * alpha

    blend = cv2.resize(blend, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_LINEAR)[:, :, np.newaxis]
    heatmap = (blend * prediction_int + (1 - blend) * image).astype(np.uint8)
    return heatmap

@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        VIDEOS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            # 'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book added!'
    else:
        response_object['books'] = VIDEOS
    return jsonify(response_object)



if __name__ == '__main__':
    app.run(host= '0.0.0.0', port="7272")
