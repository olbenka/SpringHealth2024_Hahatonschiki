<template>
    <div>
        <q-card class="q-pa-md">
            <q-card-section>
                <div class="text-h6">Метрики спринта</div>
            </q-card-section>

            <q-card-section class="row q-gutter-md">
                <q-select class="col-12 col-md-4" v-model="selectedSprints" label="Выберите спринты"
                    :options="sprintOptions" emit-value map-options multiple use-chips />

                <q-select class="col-12 col-md-4" v-model="selectedTeams" label="Выберите команды"
                    :options="teamOptions" emit-value map-options multiple use-chips />

                <q-btn @click="fetchMetrics" label="Ок" color="primary" class="col-12 col-md-2" />

                <!-- Настраиваемые параметры -->
                <q-btn @click="showSettings = true" label="Настройки" color="secondary" class="col-12 col-md-2" />
            </q-card-section>

            <!-- Слайдер для выбора промежутка времени -->
            <q-card-section v-if="timeRange">
                <q-slider v-model="selectedTimeRange" :min="timeRange.min" :max="timeRange.max" :step="86400000"
                    label-always range :label-value="formatDateRange" />
            </q-card-section>

            <!-- Диалог настроек -->
            <q-dialog v-model="showSettings">
                <q-card style="min-width: 300px;">
                    <q-card-section>
                        <div class="text-h6">Настройки расчёта метрик</div>
                    </q-card-section>
                    <q-card-section class="q-gutter-md">
                        <q-input v-model.number="settings.completionThreshold" type="number"
                            label="Порог выполнения (%)" />
                        <q-input v-model.number="settings.maxPenalty" type="number" label="Максимальный штраф (%)" />
                        <!-- Добавьте дополнительные настройки по необходимости -->
                    </q-card-section>
                    <q-card-actions align="right">
                        <q-btn flat label="Отмена" v-close-popup />
                        <q-btn flat label="Сохранить" @click="saveSettings" />
                    </q-card-actions>
                </q-card>
            </q-dialog>

            <!-- Отображение метрик для каждого спринта -->
            <div v-for="(metricData, index) in metricsList" :key="index" class="q-mt-md">
                <q-card-section>
                    <div class="text-h6">Спринт: {{ metricData.sprintName }}</div>
                </q-card-section>

                <div class="q-mt-md">
                    <q-linear-progress :value="metricData.progressValue" color="primary" size="lg" animated />
                    <div class="text-subtitle1 q-mt-sm">
                        Прогресс спринта: {{ (metricData.progressValue * 100).toFixed(2) }}%
                    </div>
                </div>

                <div class="q-mt-md">
                    <q-card>
                        <q-card-section>
                            <div class="text-h6">Индекс Здоровья Спринта: {{ metricData.metrics.sprint_health_index }}%
                            </div>
                        </q-card-section>
                    </q-card>
                </div>

                <div class="q-mt-md" style="height: 400px;">
                    <BarChart :chart-data="metricData.chartData" />
                </div>

                <div class="q-mt-md" style="height: 400px;">
                    <LineChart :chart-data="metricData.lineChartData" />
                </div>

                <div class="q-mt-md">
                    <q-card>
                        <q-card-section>
                            <div class="text-h6">Дополнительные Метрики</div>
                        </q-card-section>
                        <q-card-section>
                            <div>Процент выполнения: {{ metricData.metrics.completion_percentage }}%</div>
                            <div>Средняя длительность выполнения задач: {{ metricData.metrics.average_task_duration }}
                                часов</div>
                            <div>Добавлено задач после начала спринта: {{ metricData.metrics.added_tasks_after_start }}
                            </div>
                            <div>
                                Исключённые задачи: {{ metricData.metrics.excluded_tasks.count }} ({{
                                    metricData.metrics.excluded_tasks.hours }} часов)
                            </div>
                            <div>Задачи, завершённые в последний день: {{ metricData.metrics.last_day_done_percentage
                                }}%</div>
                        </q-card-section>
                    </q-card>
                </div>

                <div class="q-mt-md">
                    <q-card>
                        <q-card-section>
                            <div class="text-h6">Успешность Спринта</div>
                        </q-card-section>
                        <q-card-section class="row q-gutter-md">
                            <q-banner class="col-12 col-md-6"
                                :color="getStatusColor(metricData.metrics.backlog_changed_percentage, 20, 50)"
                                text-color="white">
                                Бэклог изменен: {{ metricData.metrics.backlog_changed_percentage }}%
                            </q-banner>
                            <q-banner class="col-12 col-md-6"
                                :color="getStatusColor(metricData.metrics.to_do_percentage, 20)" text-color="white">
                                К выполнению: {{ metricData.metrics.to_do_percentage }}%
                            </q-banner>
                            <q-banner class="col-12 col-md-6"
                                :color="getStatusColor(metricData.metrics.removed_percentage, 10)" text-color="white">
                                Снято: {{ metricData.metrics.removed_percentage }}%
                            </q-banner>
                            <q-banner class="col-12 col-md-6"
                                :color="getStatusColor(metricData.metrics.last_day_done_percentage, 50)"
                                text-color="white">
                                Задачи, завершённые в последний день: {{ metricData.metrics.last_day_done_percentage }}%
                            </q-banner>
                        </q-card-section>
                    </q-card>
                </div>
            </div>
        </q-card>

        <!-- Диалог загрузки -->
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
import BarChart from './BarChart.vue';
import LineChart from './LineChart.vue';
import { Notify } from 'quasar';

export default defineComponent({
    name: 'MetricsDisplay',
    components: {
        BarChart,
        LineChart,
    },
    data() {
        return {
            sprints: [],
            selectedSprints: [],
            metricsList: [],
            loading: false,
            timeRange: null,
            selectedTimeRange: null,
            teams: [],
            selectedTeams: [],
            settings: {
                completionThreshold: 80,
                maxPenalty: 20,
            },
            showSettings: false,
        };
    },
    computed: {
        sprintOptions() {
            return this.sprints.map((sprint) => ({
                label: sprint.sprint_name,
                value: sprint.sprint_id,
                startDate: new Date(sprint.start_date),
                endDate: new Date(sprint.end_date),
            }));
        },
        teamOptions() {
            return this.teams.map((team) => ({
                label: team.name,
                value: team.id,
            }));
        },
        formatDateRange() {
            const [start, end] = this.selectedTimeRange;
            return `${new Date(start).toLocaleDateString()} - ${new Date(end).toLocaleDateString()}`;
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
        async fetchTeams() {
            try {
                const response = await axios.get('http://localhost:8001/teams/');
                this.teams = response.data;
            } catch (error) {
                Notify.create({
                    type: 'negative',
                    message: `Ошибка при получении списка команд: ${error.response ? error.response.data.detail : error.message
                        }`,
                });
            }
        },
        async fetchMetrics() {
            if (this.selectedSprints.length === 0) return;

            this.loading = true;
            this.metricsList = [];

            for (const sprintId of this.selectedSprints) {
                try {
                    // Получаем выбранный спринт для получения дат
                    const sprint = this.sprintOptions.find((s) => s.value === sprintId);

                    // Если слайдер не был инициализирован, инициализируем его
                    if (!this.timeRange) {
                        this.timeRange = {
                            min: sprint.startDate.getTime(),
                            max: sprint.endDate.getTime(),
                        };
                        this.selectedTimeRange = [this.timeRange.min, this.timeRange.max];
                    }

                    // Формируем параметры запроса
                    const params = {
                        teams: this.selectedTeams,
                        start_date: new Date(this.selectedTimeRange[0]).toISOString(),
                        end_date: new Date(this.selectedTimeRange[1]).toISOString(),
                        settings: this.settings,
                    };

                    const response = await axios.get(`http://localhost:8001/sprints/${sprintId}/metrics`, { params });

                    const metrics = response.data;

                    // Подготовка данных для отображения
                    const metricData = {
                        sprintName: sprint.label,
                        metrics,
                        progressValue: metrics.completion_percentage / 100,
                        chartData: this.getChartData(metrics),
                        lineChartData: this.getLineChartData(metrics),
                    };

                    this.metricsList.push(metricData);
                } catch (error) {
                    Notify.create({
                        type: 'negative',
                        message: `Ошибка при получении метрик: ${error.response ? error.response.data.detail : error.message
                            }`,
                    });
                }
            }

            this.loading = false;
        },
        getChartData(metrics) {
            return {
                labels: ['К выполнению', 'В работе', 'Сделано', 'Снято', 'Заблокировано'],
                datasets: [
                    {
                        label: 'Часы',
                        backgroundColor: ['#f44336', '#ff9800', '#4caf50', '#9e9e9e', '#2196f3'],
                        data: [
                            metrics.to_do,
                            metrics.in_progress,
                            metrics.done,
                            metrics.removed,
                            metrics.blocked_tasks,
                        ],
                    },
                ],
            };
        },
        getLineChartData(metrics) {
            if (metrics.done_tasks_over_time) {
                const dates = Object.keys(metrics.done_tasks_over_time).sort();
                const values = dates.map((date) => metrics.done_tasks_over_time[date]);

                return {
                    labels: dates,
                    datasets: [
                        {
                            label: 'Сделано задач',
                            backgroundColor: '#4caf50',
                            borderColor: '#4caf50',
                            data: values,
                            fill: false,
                        },
                    ],
                };
            }
            return null;
        },
        getStatusColor(value, threshold1, threshold2 = null) {
            if (threshold2 !== null) {
                if (value <= threshold1) return 'green-4';
                if (value > threshold1 && value <= threshold2) return 'yellow-4';
                return 'red-4';
            } else {
                if (value <= threshold1) return 'green-4';
                return 'red-4';
            }
        },
        saveSettings() {
            this.showSettings = false;
            this.fetchMetrics();
        },
    },
    mounted() {
        this.fetchSprints();
        this.fetchTeams();
    },
});
</script>

<style scoped></style>