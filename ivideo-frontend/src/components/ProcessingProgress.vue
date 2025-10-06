<template>
  <div class="processing-progress">
    <el-progress 
      :percentage="percentage" 
      :status="status"
      :show-text="true"
    />
    <div class="progress-info">
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessingProgress',
  props: {
    percentage: {
      type: Number,
      default: 0
    },
    status: {
      type: String,
      default: undefined
    },
    message: {
      type: String,
      default: '处理中...'
    }
  }
}
</script>

<style scoped>
.processing-progress {
  padding: 20px;
}

.progress-info {
  text-align: center;
  margin-top: 10px;
}

.progress-info p {
  font-size: 14px;
  color: #909399;
}
</style>