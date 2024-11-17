<template>
    <div>
        <q-card class="q-pa-md">
            <q-card-section>
                <div class="text-h6">Метрики спринта</div>
            </q-card-section>

            <q-card-section>
                <q-select v-model="selectedSprint" label="Выберите спринт" :options="sprintOptions" emit-value
                    map-options @input="fetchMetrics" />
            </q-card-section>

            <q-card-section v-if="metrics">
                <div class="q-mt-md">
                    <q-linear-progress :value="progressValue" color="primary" size="lg" animated />
                    <div class="text-subtitle1 q-mt-sm">Прогресс спринта: {{ progressValue * 100 }}%</div>
                </div>

                <div class="q-mt-md">
                    <bar-chart :chart-data="chartData" />
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

        <q-notify v-if="notification" :message="notification.message" :color="notification.color" timeout="3000" />
    </div>
</template>

<script>
import axios from 'axios';
import { Bar } from 'vue-chartjs';

export default {
    name: 'MetricsDisplay',
    components: {
        BarChart: {
            extends: Bar,
            props: ['chartData'],
            mounted() {
                this.renderChart(this.chartData, { responsive: true, maintainAspectRatio: false });
            },
            watch: {
                chartData(newData) {
                    this.renderChart(newData, { responsive: true, maintainAspectRatio: false });
                },
            },
        },
    },
    data() {
        return {
            sprints: [],
            selectedSprint: null,
            metrics: null,
            chartData: null,
            loading: false,
            notification: null,
        };
    },
    computed: {
        sprintOptions() {
            return this.sprints.map(sprint => ({
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
                this.notification = {
                    message: `Ошибка при получении списка спринтов: ${error.response ? error.response.data.detail : error.message}`,
                    color: 'red',
                };
            }
        },
        async fetchMetrics() {
            if (!this.selectedSprint) return;

            this.loading = true;
            this.notification = null;

            try {
                const response = await axios.get(`http://localhost:8001/sprints/${this.selectedSprint}/metrics`);
                this.metrics = response.data;
                this.updateChartData();
            } catch (error) {
                this.notification = {
                    message: `Ошибка при получении метрик: ${error.response ? error.response.data.detail : error.message}`,
                    color: 'red',
                };
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
};
</script>

<style scoped></style>