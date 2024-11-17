<template>
  <q-page padding>
    <q-dialog v-model="loading">
      <q-card>
        <q-card-section>
          <div class="text-h6">Загрузка файлов...</div>
        </q-card-section>
        <q-linear-progress indeterminate color="primary" />
      </q-card>
    </q-dialog>
    <div class="text-center text-h5"><q-img style="height: 100px; max-width: 110px" src="~assets/t1.png"></q-img>
      <div class="text-bold">SprintHealth</div>
      <div>Вся правда о спринтах в одном клике от Вас!</div>
    </div>

    <div class="row" style="background-image:url('/src/assets/fon.png'); height:400px" v-if="!showMetrics">

      <div class="q-pa-md q-mx-auto col-3">
        <div>
          <div class="text-h6 q-mx-xl" style="color:white">Загрузка CSV файлов</div>
        </div>

        <div>
          <q-uploader url="" ref="uploader" label="Перетащите файлы сюда или нажмите для выбора"
            hint="Можно загрузить несколько файлов" multiple accept=".csv" @added="onFilesAdded" />
          <q-btn class="q-my-sm" label="Загрузить" color="primary" @click="uploadFiles"
            :disable="files.length === 0 || loading" />
        </div>

      </div>
    </div>
    <metrics-display v-else />


  </q-page>
</template>

<script>
import axios from 'axios';
import { Notify } from 'quasar';
import MetricsDisplay from 'components/MetricsDisplay.vue';

export default {
  name: 'IndexPage',
  components: {
    MetricsDisplay,
  },
  data() {
    return {
      showMetrics: false,
      files: [],
      loading: false,
    };
  },
  methods: {
    onFilesAdded(newFiles) {
      console.log('Добавленные файлы:', newFiles);
      this.files = newFiles;
    },
    async uploadFiles() {
      if (this.files.length === 0) return;

      this.loading = true;

      try {
        for (let file of this.files) {
          const formData = new FormData();
          formData.append('file', file);

          let uploadUrl = '';
          if (file.name.includes('entities')) {
            uploadUrl = 'http://localhost:8001/upload/entities';
          } else if (file.name.includes('history')) {
            uploadUrl = 'http://localhost:8001/upload/history';
          } else if (file.name.includes('sprints')) {
            uploadUrl = 'http://localhost:8001/upload/sprints';
          } else {
            throw new Error(`Неизвестный тип файла: ${file.name}`);
          }

          await axios.post(uploadUrl, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
        }

        Notify.create({
          message: 'Файлы успешно загружены и обработаны.',
          color: 'green',
          position: 'top',
          timeout: 3000,
        });

        this.files = [];
        this.$refs.uploader.reset();
        this.showMetrics = true;
      } catch (error) {
        console.error('Ошибка при загрузке файлов:', error);
        Notify.create({
          message: `Ошибка при загрузке файлов: ${error.response ? error.response.data.detail : error.message
            }`,
          color: 'red',
          position: 'top',
          timeout: 5000,
        });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped></style>
