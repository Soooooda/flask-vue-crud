# Metis Server
### Build
1. Download the project
    ```sh
    $ git clone https://gitlab-master.nvidia.com/Desktop-Notebook-Performance-Team-Shanghai/metis-server.git
    ```
2. Create some folders
    ```sh
    $ cd metis-server
    $ mkdir assets
    $ cd assets
    $ mkdir videos
    $ mkdir images
    $ mkdir csvs
    $ mkdir frames
    $ mkdir json
    ```
3. Deploy backend -- Flask
    ```sh
    $ ps aux | grep gunicorn
    $ kill -9 process_id # the process id from output of last command
    $ cd /metis-server/server/
    $ conda activate metis
    $ conda install requirements.txt
    $ nohup gunicorn --keep-alive 1000000 --timeout 1000000 -c gunicorn.py ini app:app &
    ```
    * Remember to change the path in App.py in the server folder.
    * The log is located in server/nohup.out.
    * Add a /models director under /server. The models are not available...

4. Deploy frontend -- Vue
    ```sh
    $ cd /metis-server/client/
    $ sudo su
    $ npm install -g cnpm --registry=https://registry.npm.taobao.org
    $ npm config set registry https://registry.npm.taobao.org
    $ npm install
    ```
    * open all the ip address emerged in the /client/src/components/Books.vue to your current ip address.

    ```sh
    $ npm run build # here will create a dist directory automatically
    ```
    

5. Deploy Nginx
    * The default file is as followed. Also need to change the path.
    ```yaml
        server {
        listen 8080;
        listen [::]:8080;

        server_name localhost;

        location / {
            client_max_body_size  10G; 
            proxy_connect_timeout 5000s; 
            proxy_read_timeout 5000s; 
            root /home/test/Desktop/flask-vue-crud/client/dist/; //here you need to change the path to the dist file
            error_page 405 =200 http://$host$request_uri;
            index index.html;
        }
        

        add_header Access-Control-Allow-Origin *;

        location /images/ {
            client_max_body_size  10G;
            proxy_connect_timeout 5000s; 
            proxy_read_timeout 5000s;  
            alias /home/test/Desktop/flask-vue-crud/assets/heatmaps/; ////here you need to change the path to the heatmap file
            error_page 405 =200 http://$host$request_uri;
            autoindex on;
        }

        location /videos/ {
            client_max_body_size  10G; 
            proxy_connect_timeout 5000s; 
            proxy_read_timeout 5000s; 
            alias /home/test/Desktop/flask-vue-crud/assets/videos/; //here you need to change the path to the videos file
            error_page 405 =200 http://$host$request_uri;
            autoindex on;
        }

        location /frames/ {
            client_max_body_size  10G; 
            proxy_connect_timeout 5000s; 
            proxy_read_timeout 5000s; 
            alias /home/test/Desktop/flask-vue-crud/assets/frames/; //here you need to change the path to the frames file
            error_page 405 =200 http://$host$request_uri;
            autoindex on;
        }
        
    }
    server {
        listen 5000;
        
        server_name localhost;

        location / {
            proxy_connect_timeout 5000s; 
            proxy_read_timeout 5000s; 
            client_max_body_size  10G; 
            proxy_pass http://10.19.199.137:7272;//here you need to change the ip to your ip
            error_page 405 =200 $uri;
        }


    }

    ```
    * Then Start nginx service.
    ```sh
    $ service nginx restart
    ```
6. Access http://your_ip:8080.
    * If you want to test two models togther, it's recommanded that you upload different copies of the video clips.
    * The website is a single-process application. So you need to wait for a task done and then do the next.
    * You can refresh the website when a task is done if the corresponding picture is not shown when the mouse is on the linechart.

### Troubleshoot
1. Try 'sudo su' whenever permission denied.
2. If you want to test the flask api, you can use the following command under the server folder.
```sh
    gunicorn --keep-alive 1000000 --timeout 1000000 -c gunicorn.py ini app:app
```

