<template>
    <div>
        <q-card class="q-pa-md">
            <q-card-section>
                <div class="text-h6">Загрузка CSV файлов</div>
            </q-card-section>

            <q-uploader url="" ref="uploader" label="Перетащите файлы сюда или нажмите для выбора"
                hint="Можно загрузить несколько файлов" multiple accept=".csv" @added="onFilesAdded" />

            <q-card-actions align="right">
                <q-btn label="Загрузить" color="primary" @click="uploadFiles"
                    :disable="files.length === 0 || loading" />
            </q-card-actions>
        </q-card>

        <!-- Диалог загрузки -->
        <q-dialog v-model="loading">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Загрузка файлов...</div>
                </q-card-section>
                <q-linear-progress indeterminate color="primary" />
            </q-card>
        </q-dialog>
    </div>
</template>

<script>
import axios from 'axios';
import { Notify } from 'quasar';

export default {
    name: 'UploadFiles',
    data() {
        return {
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
                // Отправляем файлы поочередно
                for (let file of this.files) {
                    const formData = new FormData();
                    formData.append('file', file);

                    // Определяем, к какому эндпоинту отправлять файл
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
