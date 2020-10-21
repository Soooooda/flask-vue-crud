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
# import redis
from flask_session import Session
from glob import glob
import json
from collections import namedtuple

# models
HeatmapParams = namedtuple("HeatmapParams", 
                          ["vmin", "vmax", "alpha", "adapt_transperancy"])
params_mapping = {"DLSS": 
                      HeatmapParams(vmin=0, vmax=10.0, alpha=0.5, adapt_transperancy=False),
                 "OPS": 
                      HeatmapParams(vmin=-20, vmax=20.0, alpha=0.5, adapt_transperancy=False)}
methods_mapping = {"DLSS": "dense_prediction",
                   "OPS": "forward",
                  }

UPLOAD_FOLDER = '../assets/'
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

# the redis part didn't work 用于登录注册
# app.config['SECRET_KEY'] = 'wozaiperflabdagong2'
# app.config['SESSION_USE_SIGNER'] = True  # 是否对发送到浏览器上session的cookie值进行加密
# app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
# app.config['SESSION_KEY_PREFIX'] = 'session:'  # 保存到session中的值的前缀
# app.config['PERMANENT_SESSION_LIFETIME'] = 7200  # 失效时间 秒
# app.config['SESSION_REDIS'] = redis.Redis.from_url("redis://0.0.0.0:6379")  # redis数据库连接

# 绑定flask 对象
f_session.init_app(app)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
app.logger.info('Metis服务启动')

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


# Load the videos
VIDEOS = []
Video_arr = []
Video_dir = UPLOAD_FOLDER

types = ('*.mp4', '*.mkv') # the tuple of file types
for files in types:
    Video_arr.extend(glob(os.path.join(Video_dir,'videos/'+ files)))

app.logger.info('读取已有的视频')
for v in Video_arr:
    title = v.split('/')[-1].split('.')[0]
    # print(v)
    
    vi = {}
    vi['id'] = uuid.uuid4().hex
    vi['title'] = title
    vi['read'] = False
    vi['time'] = int(os.stat(v).st_size*386/32115808)
    vi['progress'] = 0
    vi['model'] = 'DLSS'
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],'json/'+ title+'_DLSS.json')) or os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],'json/'+ title+'_OPS.json')):
        vi['read'] = True
        vi['progress'] = vi['time']
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'],'json/'+ title+'_OPS.json')):
            vi['model'] = 'OPS'
    VIDEOS.append(vi)
    app.logger.info('视频：%s,是否分析过：%r,时间: %d sec,模型: %s',v,vi['read'],vi['time'],vi['model'])

# 0 成功
# -1 用户名或密码错误
# 登录功能，没有使用
@app.route('/login', methods=['GET', 'POST'])
def login():
    response_object = {'status': '-1'}
    if request.method == 'POST':
        post_data = request.get_json()
        userName = post_data.get('username')
        pwd = post_data.get('password')
        if userName == USERNAME and pwd == PWD:
            response_object['status'] = '0'
            session['status'] = '0'
        else:
            session['status'] = '-1'
    else:
        if 'status' in session and session['status'] == '0':
            response_object['status'] = '0'
        else:
            response_object['status'] = '-1'
    return jsonify(response_object)

# 登录功能，没有使用
@app.route('/getsession', methods=['GET', 'POST'])
def getsession():
    response_object = {'status': session['test10111']}
    return jsonify(response_object)

def remove_book(book_id):
    for book in VIDEOS:
        if book['id'] == book_id:
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+book['title']+'.mp4')):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+book['title']+'.mp4'))
            if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], 'frames/'+book['title'])):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'frames/'+book['title']))
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+book['title']+'_DLSS.json')):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+book['title']+'_DLSS.json'))
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+book['title']+'_OPS.json')):
                os.system("rm -rf " + os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+book['title']+'_OPS.json'))
            VIDEOS.remove(book)
            return True
    return False

@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        Need2Analyze = True
        for book in VIDEOS:
            if book['id'] == book_id:
                if book['read']==True:
                    Need2Analyze = False
                book['read'] = Need2Analyze
                book['model'] = post_data.get('model')

        if Need2Analyze==True:# 需要分析
            
            #是否处理成帧过
            if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], 'frames/'+post_data.get('title')))!=True:
                path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+post_data.get('title')+'.mp4')
                
                vidcap = cv2.VideoCapture(path)
                success2,image2 = vidcap.read()
                count = 0
                app.logger.info("开始把视频处理成帧, 是否成功：%r(该步骤很慢)",success2)
                os.system('mkdir '+os.path.join(app.config['UPLOAD_FOLDER'],'frames/'+post_data.get('title')))
                while success2:
                    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], "frames/"+post_data.get('title')+"/frame%d.png" % count), image2)
                    success2,image2 = vidcap.read()
                    count += 1
                app.logger.info("一共处理了%d帧",count)
            # turn frames into JSONs
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+post_data.get('title')+'_'+post_data.get('model')+'.json'))!=True:
                frames2Score(post_data.get('title'),post_data.get('model'))

        else: # 需要删掉分析
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+post_data.get('title')+'_'+post_data.get('model')+'.json')):
                os.system("rm " + os.path.join(app.config['UPLOAD_FOLDER'], 'json/'+post_data.get('title')+'_'+post_data.get('model')+'.json'))
                app.logger.info("删除分析过的文件成功")

        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        if(remove_book(book_id)):
            app.logger.info("删除视频成功！")
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)

# test
@app.route('/result',methods=['GET'])
def result():
    print ("test")
    return "File Uploaded Successfully"

#Upload Video
@app.route('/upload/video',methods=['GET','POST'])
def uploadVideo():
    if request.method == 'POST':
        
        file = request.files['file']
        filename = secure_filename(file.filename)
        app.logger.info("开始上传视频：%s",file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos/'+filename)
        file.save(path)
        # get file size
        # size = os.stat(path).st_size
        # app.logger.info("视频大小：%d",size)
        return jsonify({'status':filename.split('.')[0]})


#Upload Scenes
@app.route('/upload/scene/<model>',methods=['GET','POST'])
def uploadScene(model):
    if request.method == 'POST':
        
        path = os.path.join(app.config['UPLOAD_FOLDER'], 'images/')
        f = request.files['file']
        # model = request.get_json()['model']
        app.logger.info("开始上传图片：%s",f.filename)

        f.save(path+f.filename)

        path = f.filename.split('.')[0] + '_'+model+'_result.png'
        print('path2:')
        print(path)
        if os.path.isfile(path):
            os.system("rm "+path)

        iq = image2Score(f.filename,model)
        # path = f.filename.split('.')[0] + '_result.png'
        return jsonify({'iq':str(iq), 'path':path})
        
#Analyze Videos
@app.route('/analysis',methods=['GET','POST'])
def analyzeFile():
    if request.method == 'GET':
        IQ_SCORE = []
        json_path = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'],'json/'))
        for j in json_path:
            f = open(os.path.join(app.config['UPLOAD_FOLDER'],'json/'+j))
            json_string= json.load(f)
            IQ_SCORE.append(json_string)
            f.close()
        app.logger.info("IQ score上传成功")
        return jsonify(IQ_SCORE)

def frames2Score(frame,model):
    app.logger.info("开始部署模型(该步骤很慢)")
    trace_path = ""
    method = ""
    if model=="DLSS":
        trace_path = "models/model_dlss.pt"
        method = "dense_prediction"
    else:
        trace_path = "models/model_ops.pt"
        method = "forward"
    device = "cuda"
    frame_dir = os.path.join(app.config['UPLOAD_FOLDER'],'frames/'+frame)
    result_dir = os.path.join(app.config['UPLOAD_FOLDER'],'json/'+frame+'_'+model+'.json')

    model = torch.jit.load(trace_path, map_location=device)

    model.eval()
    model.requires_grad = False
    images_folder = Path(frame_dir)
    dataset = FromFolder(folder=images_folder)
    result = process_dataset(model=model, dataset=dataset, batch_size=1,
                            num_workers=2, device=device,
                            output_key=1,
                            method=method,  # method="forward" for metis_ops_current
                            )
    with open(result_dir, 'w') as f:
        json.dump(result, f)
        app.logger.info("存储IQ Score成功")
    return result


DEFAULT_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # imagenet normalization
])

def display_prediction(img_orig, score):
    img = img_orig.copy()
    return img

def predict_on_image(model, method, img, transform, device):
    processed_img = transform(img).unsqueeze(0).to(device)
    
    if method is not None:
        output = getattr(model, method)(processed_img)
    else:
        output = model(processed_img)
    
    heatmap_raw, score = output
    return heatmap_raw.cpu().detach().numpy(), score.cpu().detach().item()

def full_predict(model_name,image_path, model, method, heatmap_params, res_folder, device, transform=DEFAULT_TRANSFORM):
    image = cv2.cvtColor(cv2.imread(str(image_path)), cv2.COLOR_BGR2RGB)
    hm_raw, score = predict_on_image(model=model, method=method, img=image, transform=transform, device=device)
    
    heatmap = generate_heatmap(dense_prediction=hm_raw, image=image,
                              vmin=heatmap_params.vmin, vmax=heatmap_params.vmax,
                              alpha=heatmap_params.alpha, adapt_transperancy=heatmap_params.adapt_transperancy)
    
    heatmap_with_score = display_prediction(heatmap, score)
    print(os.path.join(app.config['UPLOAD_FOLDER'], 'heatmaps/')+image_path.split('/')[-1].split('.')[0]+'_'+model_name+"_result.png")
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'heatmaps/')+image_path.split('/')[-1].split('.')[0]+'_'+model_name+"_result.png", heatmap_with_score[..., ::-1])
        
    return score




def image2Score(path,model):
    app.logger.info("image2score:%s",model)
    if model=="DLSS":
        trace_path = "models/model_dlss.pt"#models/model.pt
        method = "dense_prediction"
    else:
        trace_path = "models/model_ops.pt"
        method = "forward"
    model_name = model
    # method = methods_mapping[model_name]
    model = torch.jit.load(trace_path, map_location="cuda")
    model.eval()
    model.requires_grad = False
    app.logger.info("模型：%s，方法：%s",model_name,method)
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'images/')+path
    device = "cuda"

    iq = full_predict(model_name= model_name,image_path=image, model=model, method=method, 
                     heatmap_params=params_mapping[model_name],
                     res_folder="", device=device)
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
        prog = 0
        # app.logger.info("update videos: 是否")
        if post_data.get('read')==True:
            prog = post_data.get('time')
        VIDEOS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'read': post_data.get('read'),
            'time': post_data.get('time'),
            'progress': prog,
            'model': post_data.get('model')
        })
        print(post_data.get('time'))
        app.logger.info("更新视频信息成功")
        response_object['message'] = 'Book added!'
    else:
        for book in VIDEOS:
            if book['read']==True:
                book['progress'] = book['time']
            else:
                book['progress'] = 0
        app.logger.info("返回视频信息成功")
        response_object['books'] = VIDEOS
    return jsonify(response_object)



if __name__ == '__main__':
    app.run(host= '0.0.0.0', port="7272")
