<!-- src/components/LineChart.vue -->
<template>
    <canvas ref="canvas"></canvas>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { Chart as ChartJS, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip } from 'chart.js';

ChartJS.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale, Tooltip);

export default defineComponent({
    name: 'LineChart',
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
                    type: 'line',
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