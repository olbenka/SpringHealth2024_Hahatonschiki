<template>
  <q-page padding>
    <div class="q-gutter-md">
      <upload-files />
      <metrics-display />
    </div>
  </q-page>
</template>

<script>
import UploadFiles from 'components/UploadFiles.vue';
import MetricsDisplay from 'components/MetricsDisplay.vue';

export default {
  name: 'IndexPage',
  components: {
    UploadFiles,
    MetricsDisplay,
  },
};
</script>

<style scoped></style>
