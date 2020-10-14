<template>
  <div class="container">
    <div class="row">
      <!-- <div> -->

        <b-overlay :show="showOverlay" rounded="sm" >

        <h1>Metis</h1>
        <hr><br><br>

        <b-alert
          :show="dismissCountDown"
          dismissible
          variant="warning"
          @dismissed="dismissCountDown=0"
          @dismiss-count-down="countDownChanged"
        >
        <b-spinner label="Spinning"></b-spinner>
        {{this.message}}
      
        </b-alert>

        <!-- <alert :message=message v-if="showMessage"></alert> -->

        <div>
          <b-tabs content-class="mt-3" justified>
            <b-tab title="Single Scene" active>
              <!-- <h2>Single Scene</h2> -->
              
              <b-form method=post enctype=multipart/form-data @submit="uploadScene">
                  <b-form-group label="Image" label-for="scene" label-cols-lg="2">
                    <b-input-group>
                      <b-input-group-prepend is-text>
                        <!-- <b-icon icon="image-fill"></b-icon> -->
                      </b-input-group-prepend>
                      
                      <b-form-file id="scene" type=file name=file :disabled="busy" ></b-form-file>
                      <!-- accept="image/*" -->                    
                    </b-input-group>
                  </b-form-group>
                  <div class="d-flex justify-content-center">
                      <b-button ref="submit" type="submit" :disabled="busy">Submit</b-button>
                  </div>
              </b-form>

              <h5>Heatmap:</h5>
              <b-img v-if="this.SceneURL" :key="this.SceneURL" :src="this.SceneURL" fluid-grow alt="Responsive image"></b-img>
              <h5>Score:</h5>
              <span>{{ Scene_IQ }}</span>
            </b-tab>

            <b-tab title="Video Frames">
              <!-- <b-table striped hover :items="items"></b-table>
              <tr v-for="button in buttons" :key="button.id">
                <td>
                    <button @click="button.method">{{button.name}}</button>
                </td>
              </tr> -->

          <!-- <alert :message=message v-if="showMessage"></alert> -->
          <button type="button" class="btn btn-success btn-sm" v-b-modal.book-modal>Add Video</button>
          <br><br>
          <b-overlay :show="blockUser" rounded="sm">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th scope="col">Title</th>
                  <!-- <th scope="col">Author</th> -->
                  <th scope="col">Analyzed?</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(book, index) in books" :key="index">
                  <td>{{ book.title }}</td>
                  <!-- <td>{{ book.author }}</td> -->
                  <td>
                    <span v-if="book.read">Yes</span>
                    <span v-else>No</span>
                  </td>
                  <td>
                    <div class="btn-group" role="group">
                      <button
                              type="button"
                              class="btn btn-warning btn-sm"
                              v-b-modal.book-update-modal
                              @click="editBook(book)">
                          Analyze
                      </button>
                      <button
                              type="button"
                              class="btn btn-danger btn-sm"
                              @click="onDeleteBook(book)">
                          Delete
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </b-overlay>


              <b-modal ref="addBookModal"
                      id="book-modal"
                      title="Add a new book"
                      hide-footer>


                <b-form method=post enctype=multipart/form-data @submit="uploadVideo"   @reset="onReset" style="padding-bottom: 20px">
                    <b-form-group label="Mp4 Video" label-for="file" label-cols-lg="2">
                      <b-input-group>
                        <b-input-group-prepend is-text>
                          <!-- <b-icon icon="image-fill"></b-icon> -->
                        </b-input-group-prepend>                      
                        <b-form-file id="file" type=file name=file :disabled="busy" ></b-form-file>                    
                      </b-input-group>
                    </b-form-group>
                    <div class="d-flex justify-content-center">
                        <b-button ref="submit" type="submit" variant="primary">Submit</b-button>
                    </div>
                </b-form>
              </b-modal>

              <!-- uploadVideo -->

              <div class="row">
                <div class="col-sm-6"><b-button variant="outline-primary" type="button" v-on:click="onAnalyze">Output Linechart</b-button></div>               
                <div class="col-sm-6">This Scene: {{this.imgName}}</div>
              </div>
              <div class="row">
                <div id="main" class="col-sm-6"></div>
                <b-img :src="this.img.ImgURL" :key="this.img.ImgURL" class="col-sm-6"></b-img>
              </div>
            </b-tab>
          </b-tabs>
        </div>

        <template v-slot:overlay>
          <div>
            <b-form class="position-relative p-3" @submit="onLogin">
              <h3 class="justify-content-center" >Sign In</h3>
              <b-form-group label="username" label-for="username" label-cols-lg="2">
                <b-input-group>
                  <b-input-group-prepend is-text>
                    <b-icon icon="person-fill"></b-icon>
                  </b-input-group-prepend>
                  <b-form-input v-model="userForm.username" id="username" type="username" :disabled="busy"></b-form-input>
                </b-input-group>
              </b-form-group>
              <b-form-group label="password" label-for="password" label-cols-lg="2">
                <b-input-group>
                  <b-input-group-prepend is-text>
                    <b-icon icon="envelope-fill"></b-icon>
                  </b-input-group-prepend>
                  <b-form-input v-model="userForm.password" id="password" type="password" :disabled="busy"></b-form-input>
                </b-input-group>
              </b-form-group>
              <div class="d-flex justify-content-center">
                <b-button ref="submit" type="submit" :disabled="busy">Submit</b-button>
              </div>
            </b-form>
            
          </div>
        </template>
      </b-overlay>
    </div>

  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert.vue';
// axios.defaults.withCredentials = true;
// // axios.defaults.headers.post['Access-Control-Allow-Origin'] = 'http://10.19.199.137';
// axios.defaults.headers.common['Authorization'] = 'wozaiperflabdagong2';

export default {
  data() {
    return {
      books: [],
      userForm: {
        username: '',
        password: '',
      },
      addBookForm: {
        title: '',
        // author: '',
        read: [],
      },
      message: '',
      showMessage: false,
      editForm: {
        id: '',
        title: '',
        // author: '',
        read: [],
      },
      file: null,
      chartData: {
        columns: [],
        rows: [],
      },
      img: {
        ImgURL: require('@/assets/icon.png'),
      },
      SceneURL: require('@/assets/Scenes/result.png'),
      busy: false,
      processing: false,
      counter: 1,
      interval: null,
      Scene_IQ: '0',
      dismissSecs: 5,
      dismissCountDown: 0,
      imgName: 0,
      showOverlay: false,
      blockUser: false,
    };
  },
  beforeDestroy() {
    this.clearInterval();
  },
  components: {
    alert: Alert,
  },
  methods: {
    // for the wait alert
    countDownChanged(dismissCountDown) {
        this.dismissCountDown = dismissCountDown;
    },
    showAlert() {
      this.dismissCountDown = this.dismissSecs;
    },
    // for the failed alert
    clearInterval() {
      if (this.interval) {
        clearInterval(this.interval);
        this.interval = null;
      }
    },
    onShown() {
      // Focus the dialog prompt
      this.$refs.dialog.focus();
    },
    onHidden() {
      // In this case, we return focus to the submit button
      // You may need to alter this based on your application requirements
      this.$refs.submit.focus();
    },
    onSubmit() {
      console.log('submit');
      this.processing = false;
      this.busy = true;
    },
    onCancel() {
      this.busy = false;
    },
    onOK() {
      // this.counter = 1
      // this.processing = true
      // // Simulate an async request
      // this.clearInterval()
      // this.interval = setInterval(() => {
      //   if (this.counter < 20) {
      //     this.counter = this.counter + 1
      //   } else {
      //     this.clearInterval()
      //     this.$nextTick(() => {
      //       this.busy = this.processing = false
      //     })
      //   }
      // }, 350);

      // this.$refs.addBookModal.hide();
      console.log('upload');
      const data = new FormData();
      data.append('foo', 'bar');
      console.log(document.getElementById('file'));
      data.append('file', document.getElementById('file').files[0]);
      // this.dismissSecs = 1;
      // this.showAlert();
      axios.post('http://10.19.199.137:5000/upload/video', data)
        .then((response) => {
          console.log(response);
        });

    },
    uploadVideo(evt) {
      // this.$refs.addBookModal.hide();
      evt.preventDefault();
      console.log('upload');
      const data = new FormData();
      data.append('foo', 'bar');
      console.log(document.getElementById('file').files[0]);
      data.append('file', document.getElementById('file').files[0]);
      this.dismissSecs = 1000000;
      // this.dismissSecs = Math.round(parseInt(document.getElementById('file').files[0].size/1024/10240));
      this.message = 'Start Uploading!';
      this.showAlert();
      // axios.post('http://10.19.199.137:5000/upload/video', data)
      //   .then((response) => {
      //     console.log(response);
      //   })
      //   .catch((error) => {
      //     // eslint-disable-next-line
      //     console.error(error);
      //   });
      var that = this;
      axios.post('http://10.19.199.137:5000/upload/video', data)
        .then((response) => {
          that.dismissSecs = 2;
          console.log(response);
          that.message = 'Finish Uploading!';
          that.showAlert();
          let read = false;
          const payload = {
            title: response.data.status,
            // author: 'anony',
            read, // property shorthand
          };
          this.addBook(payload);
          this.initForm();
        });



    },
    getBooks() {
      const path = 'http://10.19.199.137:5000/books';
      axios.get(path)
        .then((res) => {
          this.books = res.data.books;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    addBook(payload) {
      const path = 'http://10.19.199.137:5000/books';
      axios.post(path, payload)
        .then(() => {
          this.getBooks();
          this.message = 'Book added!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error);
          this.getBooks();
        });
    },
    initForm() {
      this.addBookForm.title = '';
      // this.addBookForm.author = '';
      this.addBookForm.read = [];
      this.editForm.id = '';
      this.editForm.title = '';
      // this.editForm.author = '';
      this.editForm.read = [];
    },
    onSubmitBook(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      let read = false;
      if (this.addBookForm.read[0]) read = true;
      const payload = {
        title: this.addBookForm.title,
        // author: this.addBookForm.author,
        read, // property shorthand
      };
      this.addBook(payload);
      this.initForm();
    },
    onFileChange(e) {
      console.log(e);
      const files = e.target.files || e.dataTransfer.files;
      if (!files.length) return;
      this.createFile(files[0]);
    },
    createFile(file) {
      const reader = new FileReader();
      const vm = this;
      reader.onload = (e) => {
        vm.file = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    uploadScene(evt) {
      evt.preventDefault();
      // this.$refs.addBookModal.hide();
      console.log('upload');
      const data = new FormData();
      data.append('foo', 'bar');
      console.log(document.getElementById('scene'));
      data.append('file', document.getElementById('scene').files[0]);
      // var that = this
      axios.post('http://10.19.199.137:5000/upload/scene', data)
        .then((response) => {
          console.log(response);
          this.Scene_IQ = response.data.iq;
          this.SceneURL = '/images/'+response.data.path;
          // this.message = 'Image Uploaded!';
          // this.showMessage = true;
          // this.showAlert();
          this.$bvModal.msgBoxOk(response.data.iq, {
            title: 'IQ Score',
            size: 'sm',
            buttonSize: 'sm',
            okVariant: 'success',
            headerClass: 'p-2 border-bottom-0',
            footerClass: 'p-2 border-top-0',
            centered: true
          })
        });
    },
    onAnalyze() {
      console.log('analyze');
      const path = 'http://10.19.199.137:5000/analysis';
      // this.dismissSecs = 10000000;
      // this.message = 'Start Analyzing!';
      // this.showAlert();
      axios.get(path,{timeout: 12000000})
        .then((res) => {
          // this.dismissSecs = 2
          // this.message = '     Finish Analyzing!';
          // this.showAlert();
          // this.books = res.data.books;
          console.log(res.data[0].full_path);
          // this.chartData.columns = res.data.col;
          // this.chartData.rows = res.data.ret;
          // console.log(res.data.ret);
          let echarts = require('echarts');
          const myChart = echarts.init(document.getElementById('main'));
          var url = this
          var sr = []
          res.data.forEach(function (item, index) {
            console.log(item, index);
            var line_item = {};
            line_item.name = item.full_path[0].split('/')[2];
            // index;
            line_item.data = item.predicted;
            line_item.type = 'line';
            // line_item['name'] = item.full_path[0].split('/')[2]//index;
            // line_item['data'] = item.predicted;
            // line_item['type'] = 'line';
            sr.push(line_item);
          });
          // 绘制图表
          myChart.setOption({
            // title: {
            //   text: 'Metis Score',
            // },
                dataZoom: [
                {
                    type: 'slider',
                    show: true,
                    xAxisIndex: [0],
                    // start: 1,
                    // end: 35
                },
                {
                    type: 'slider',
                    show: true,
                    yAxisIndex: [0],
                    left: '93%',
                    // start: 29,
                    // end: 36
                },
                {
                    type: 'inside',
                    xAxisIndex: [0],
                    // start: 1,
                    // end: 35
                },
                {
                    type: 'inside',
                    yAxisIndex: [0],
                    // start: 29,
                    // end: 36
                }
            ],
            tooltip: {
              trigger: 'axis',
              axisPointer: {
                type: 'cross',
              },
            },
            toolbox: {
              show: true,
              feature: {
                saveAsImage: {},
              },
            },
            xAxis: {
              type: 'category',
              data: Array.from(Array(res.data[0].full_path.length).keys()),
              // new Array(res.data.full_path.length),//res.data.full_path,
            },
            // axisPointer: {
            //   label.show: true,
            //   label: res.data.full_path,
            // },
            yAxis: {
              type: 'value',
              axisLabel: {
                formatter: '{value}',
              },
              axisPointer: {
                snap: true,
              },
            },
            series: sr,
            // series: [{
            //   name: 'predict',
            //   data: res.data[0].predicted,
            //   type: 'line',
            // }],
          });
          // myChart.on('click', 'series', function () {console.log('clicked')});

          myChart.on('mouseover', function (params) {
            // { seriesName: 'predict' }
            // series name 为 'uuu' 的系列中的图形元素被 'mouseover' 时，此方法被回调。
            console.log(parseInt(params.dataIndex, 10));
            console.log(params.seriesIndex);
            console.log(res.data[parseInt(params.seriesIndex, 10)].full_path[parseInt(params.dataIndex, 10)]);
            url.img.ImgURL = res.data[parseInt(params.seriesIndex, 10)].full_path[parseInt(params.dataIndex, 10)];
            url.imgName = parseInt(params.dataIndex, 10);
            // res.data[parseInt(params.seriesIndex)].full_path[parseInt(params.dataIndex, 10]
          });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onReset(evt) {
      evt.preventDefault();
      // this.$refs.addBookModal.hide();
      // this.initForm();
    },
    editBook(book) {
      this.blockUser = true;
      this.editForm = book;

      let read = true;
      if (this.editForm.read[0]) read = false;
      const payload = {
        title: this.editForm.title,
        read,
      };
      this.updateBook(payload, this.editForm.id);
    },
    updateBook(payload, bookID) {
      const path = `http://10.19.199.137:5000/books/${bookID}`;
      axios.put(path, payload)
        .then(() => {
          this.getBooks();
          this.blockUser = false;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.getBooks();
        });
    },
    onResetUpdate(evt) {
      evt.preventDefault();
      this.$refs.editBookModal.hide();
      this.initForm();
      this.getBooks(); // why?
    },
    removeBook(bookID) {
      const path = `http://10.19.199.137:5000/books/${bookID}`;
      axios.delete(path)
        .then(() => {
          this.getBooks();
          this.message = 'Book removed!';
          this.showMessage = true;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
          this.getBooks();
        });
    },
    onDeleteBook(book) {
      this.removeBook(book.id);
    },
    checkLogin() {
      const path = 'http://10.19.199.137:5000/login';
      var that = this;
      axios.get(path)
        .then((res) => {
          if (res.data.status === '0') that.showOverlay = false;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    onLogin(evt) {
      evt.preventDefault();
      console.log('login!');
      // const data = new FormData();
      console.log(document.getElementById('username'));
      // data.append('username', document.getElementById('username'));
      // data.append('password', document.getElementById('password'));
      const payload = {
        username: this.userForm.username,
        password: this.userForm.password,
      };
      var that = this;
      console.log(payload);
      // withCredentials: true
      axios.post('http://10.19.199.137:5000/login', payload)
        .then((response) => {
          console.log(response);
          if (response.data.status === '0') that.showOverlay = false;
        });
    },
  },
  created() {
    this.getBooks();
    // this.checkLogin();
  },
};
</script>
