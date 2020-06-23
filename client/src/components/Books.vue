<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Metis</h1>
        <hr><br><br>
        <alert :message=message v-if="showMessage"></alert>
        <h2>Upload new File</h2>
        <form method=post enctype=multipart/form-data @submit="upload">
          <input type=file name=file id="file" v-on:change="onFileChange">
           <!-- class="form-control-file bg-success" -->
          <input type=submit value=Upload class="btn btn-success btn-sm">
        </form>
        <button type="button" class="btn btn-success btn-sm" v-on:click="onAnalyze">Analyze videos</button>
        <div class="row">
          <div id="main" class="col-sm-6"></div>
          <img :src="this.img.ImgURL" class="col-sm-6"/>
        </div>
        <!-- <div id="scene" style="width: 600px;height:400px;"></div> -->
        <!-- <ve-line :data="chartData" :events="chartEvents"></ve-line> -->
        <!-- <button type="button" class="btn btn-success btn-sm" v-b-modal.book-modal>Add Book</button> -->
        <br><br>


        
        <!-- <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">Read?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="index">
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
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
                      Update
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



        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Title</th>
              <th scope="col">Author</th>
              <th scope="col">Read?</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(book, index) in books" :key="index">
              <td>{{ book.title }}</td>
              <td>{{ book.author }}</td>
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
                      Update
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
        </table> -->
      </div>
    </div>
    <b-modal ref="addBookModal"
            id="book-modal"
            title="Add a new book"
            hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
      <b-form-group id="form-title-group"
                    label="Title:"
                    label-for="form-title-input">
          <b-form-input id="form-title-input"
                        type="text"
                        v-model="addBookForm.title"
                        required
                        placeholder="Enter title">
          </b-form-input>
        </b-form-group>
        <b-form-group id="form-author-group"
                      label="Author:"
                      label-for="form-author-input">
            <b-form-input id="form-author-input"
                          type="text"
                          v-model="addBookForm.author"
                          required
                          placeholder="Enter author">
            </b-form-input>
          </b-form-group>
        <b-form-group id="form-read-group">
          <b-form-checkbox-group v-model="addBookForm.read" id="form-checks">
            <b-form-checkbox value="true">Read?</b-form-checkbox>
          </b-form-checkbox-group>
        </b-form-group>
        <b-button-group>
          <b-button type="submit" variant="primary">Submit</b-button>
          <b-button type="reset" variant="danger">Reset</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="editBookModal"
            id="book-update-modal"
            title="Update"
            hide-footer>
      <b-form @submit="onSubmitUpdate" @reset="onResetUpdate" class="w-100">
      <b-form-group id="form-title-edit-group"
                    label="Title:"
                    label-for="form-title-edit-input">
          <b-form-input id="form-title-edit-input"
                        type="text"
                        v-model="editForm.title"
                        required
                        placeholder="Enter title">
          </b-form-input>
        </b-form-group>
        <b-form-group id="form-author-edit-group"
                      label="Author:"
                      label-for="form-author-edit-input">
            <b-form-input id="form-author-edit-input"
                          type="text"
                          v-model="editForm.author"
                          required
                          placeholder="Enter author">
            </b-form-input>
          </b-form-group>
        <b-form-group id="form-read-edit-group">
          <b-form-checkbox-group v-model="editForm.read" id="form-checks">
            <b-form-checkbox value="true">Read?</b-form-checkbox>
          </b-form-checkbox-group>
        </b-form-group>
        <b-button-group>
          <b-button type="submit" variant="primary">Update</b-button>
          <b-button type="reset" variant="danger">Cancel</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
  </div>
</template>

<script>
import axios from 'axios';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      books: [],
      addBookForm: {
        title: '',
        author: '',
        read: [],
      },
      message: '',
      showMessage: false,
      editForm: {
        id: '',
        title: '',
        author: '',
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
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
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
      this.addBookForm.author = '';
      this.addBookForm.read = [];
      this.editForm.id = '';
      this.editForm.title = '';
      this.editForm.author = '';
      this.editForm.read = [];
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      let read = false;
      if (this.addBookForm.read[0]) read = true;
      const payload = {
        title: this.addBookForm.title,
        author: this.addBookForm.author,
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
    upload(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      console.log('upload');
      const data = new FormData();
      data.append('foo', 'bar');
      console.log(document.getElementById('file'));
      data.append('file', document.getElementById('file').files[0]);
      axios.post('http://10.19.199.137:5000/api/upload', data)
        .then((response) => {
          console.log(response);
          this.message = 'Videos Uploaded!';
          this.showMessage = true;
        });
    },
    onAnalyze() {
      console.log('analyze');
      const path = 'http://10.19.199.137:5000/analysis';
      axios.get(path)
        .then((res) => {
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
            line_item['name'] = index;
            line_item['data'] = item.predicted;
            line_item['type'] = 'line';
            sr.push(line_item);
          });
          // 绘制图表
          myChart.setOption({
            title: {
              text: 'Metis Score',
            },
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
              data: Array.from(Array(res.data[0].full_path.length).keys()),//new Array(res.data.full_path.length),//res.data.full_path,
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

          myChart.on('mouseover', function (params) {//{ seriesName: 'predict' }
          // series name 为 'uuu' 的系列中的图形元素被 'mouseover' 时，此方法被回调。
          console.log(parseInt(params.dataIndex));
          console.log(params.seriesIndex)
          console.log(res.data[parseInt(params.seriesIndex)].full_path[parseInt(params.dataIndex)]);
          url.img.ImgURL = require(`../assets/images/${res.data[parseInt(params.seriesIndex)].full_path[parseInt(params.dataIndex)].split('/images/')[1]}`)
          // url.getImgUrl(res.data.full_path[parseInt(params.dataIndex)].split('epic/')[1]);
          // url.img.ImgURL = res.data.full_path[parseInt(params.dataIndex)].split('epic/')[1];//parseInt(params.dataIndex)
          // console.log('hover');
          });
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addBookModal.hide();
      this.initForm();
    },
    editBook(book) {
      this.editForm = book;
    },
    onSubmitUpdate(evt) {
      evt.preventDefault();
      this.$refs.editBookModal.hide();
      let read = false;
      if (this.editForm.read[0]) read = true;
      const payload = {
        title: this.editForm.title,
        author: this.editForm.author,
        read,
      };
      this.updateBook(payload, this.editForm.id);
    },
    updateBook(payload, bookID) {
      const path = `http://10.19.199.137:5000/books/${bookID}`;
      axios.put(path, payload)
        .then(() => {
          this.getBooks();
          this.message = 'Book updated!';
          this.showMessage = true;
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
  },
  created() {
    this.getBooks();
  },
};
</script>
