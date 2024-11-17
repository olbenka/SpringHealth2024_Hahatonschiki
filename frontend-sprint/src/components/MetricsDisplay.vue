<template>
    <div>
        <q-card class="q-pa-md">
            <q-card-section>
                <div class="text-h6">Метрики спринта</div>
            </q-card-section>

            <q-card-section class="row">
                <q-select class="col-10" v-model="selectedSprint" label="Выберите спринт" :options="sprintOptions"
                    emit-value map-options />
                <q-btn @click="fetchMetrics" label="Ок" color="primary" class="col" />
            </q-card-section>

            <q-card-section v-if="metrics">
                <div class="q-mt-md">
                    <q-linear-progress :value="progressValue" color="primary" size="lg" animated />
                    <div class="text-subtitle1 q-mt-sm">
                        Прогресс спринта: {{ (progressValue * 100).toFixed(2) }}%
                    </div>
                </div>

                <div class="q-mt-md" style="height: 400px;">
                    <BarChart :chart-data="chartData" />
                </div>

                <div class="q-mt-md">
                    <q-card>
                        <q-card-section>
                            <div class="text-h6">Дополнительные Метрики</div>
                        </q-card-section>
                        <q-card-section>
                            <div>Процент выполнения: {{ metrics.completion_percentage }}%</div>
                            <div>Средняя длительность выполнения задач: {{ metrics.average_task_duration }} часов</div>
                            <div>Добавлено задач после начала спринта: {{ metrics.added_tasks_after_start }}</div>
                            <div>Исключённые задачи: {{ metrics.excluded_tasks.count }} ({{ metrics.excluded_tasks.hours
                                }} часов)</div>
                        </q-card-section>
                    </q-card>
                </div>
            </q-card-section>
        </q-card>

        <q-dialog v-model="loading">
            <q-card>
                <q-card-section>
                    <div class="text-h6">Загрузка метрик...</div>
                </q-card-section>
                <q-linear-progress indeterminate color="primary" />
            </q-card>
        </q-dialog>
    </div>
</template>

<script>
import axios from 'axios';
import { defineComponent } from 'vue';
import BarChart from './BarChart.vue'; // Убедитесь, что путь корректен
import { Notify } from 'quasar';

export default defineComponent({
    name: 'MetricsDisplay',
    components: {
        BarChart,
    },
    data() {
        return {
            sprints: [],
            selectedSprint: null,
            metrics: null,
            chartData: null,
            loading: false,
        };
    },
    computed: {
        sprintOptions() {
            return this.sprints.map((sprint) => ({
                label: sprint.sprint_name,
                value: sprint.sprint_id,
            }));
        },
        progressValue() {
            if (!this.metrics) return 0;
            const total = this.metrics.to_do + this.metrics.in_progress + this.metrics.done;
            return total ? this.metrics.done / total : 0;
        },
    },
    methods: {
        async fetchSprints() {
            try {
                const response = await axios.get('http://localhost:8001/sprints/');
                this.sprints = response.data;
            } catch (error) {
                Notify.create({
                    type: 'negative',
                    message: `Ошибка при получении списка спринтов: ${error.response ? error.response.data.detail : error.message
                        }`,
                });
            }
        },
        async fetchMetrics() {
            if (!this.selectedSprint) return;

            this.loading = true;

            try {
                const response = await axios.get(`http://localhost:8001/sprints/${this.selectedSprint}/metrics`);
                this.metrics = response.data;
                this.updateChartData();
            } catch (error) {
                Notify.create({
                    type: 'negative',
                    message: `Ошибка при получении метрик: ${error.response ? error.response.data.detail : error.message
                        }`,
                });
                this.metrics = null;
            } finally {
                this.loading = false;
            }
        },
        updateChartData() {
            this.chartData = {
                labels: ['К выполнению', 'В работе', 'Сделано', 'Снято', 'Заблокировано'],
                datasets: [
                    {
                        label: 'Часы',
                        backgroundColor: ['#f44336', '#ff9800', '#4caf50', '#9e9e9e', '#2196f3'],
                        data: [
                            this.metrics.to_do,
                            this.metrics.in_progress,
                            this.metrics.done,
                            this.metrics.removed,
                            this.metrics.blocked_tasks,
                        ],
                    },
                ],
            };
        },
    },
    mounted() {
        this.fetchSprints();
    },
});
</script>

<style scoped></style>