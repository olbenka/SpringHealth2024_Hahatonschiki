<!-- src/components/BarChart.vue -->
<template>
    <canvas ref="canvas"></canvas>
</template>

<script>
import { defineComponent, watch, ref, onMounted, onBeforeUnmount } from 'vue';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { Bar } from 'vue-chartjs';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

export default defineComponent({
    name: 'BarChart',
    props: {
        chartData: {
            type: Object,
            required: true,
        },
        options: {
            type: Object,
            default: () => ({
                responsive: true,
                maintainAspectRatio: false,
            }),
        },
    },
    setup(props) {
        const canvas = ref(null);
        let chartInstance = null;

        const renderChart = () => {
            if (canvas.value) {
                if (chartInstance) {
                    chartInstance.destroy();
                }
                chartInstance = new ChartJS(canvas.value, {
                    type: 'bar',
                    data: props.chartData,
                    options: props.options,
                });
            }
        };

        onMounted(() => {
            renderChart();
        });

        watch(
            () => props.chartData,
            () => {
                renderChart();
            },
            { deep: true }
        );

        onBeforeUnmount(() => {
            if (chartInstance) {
                chartInstance.destroy();
            }
        });

        return {
            canvas,
        };
    },
});
</script>

<style scoped>
canvas {
    width: 100% !important;
    height: 100% !important;
}
</style>