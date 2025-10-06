<template>
  <div class="project-card" @click="$emit('click')">
    <div class="project-header">
      <h3 class="project-title">{{ project.title }}</h3>
      <el-tag v-if="project.video_files.length > 0" type="success" size="small">
        {{ project.video_files.length }} 个视频
      </el-tag>
      <el-tag v-else type="info" size="small">空项目</el-tag>
    </div>
    
    <p class="project-description" v-if="project.description">
      {{ project.description }}
    </p>
    <p class="project-description" v-else>
      暂无描述
    </p>

    <div class="project-meta">
      <span class="project-date">
        创建: {{ formatDate(project.created_at) }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProjectCard',
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  emits: ['click'],
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.project-card {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.project-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  margin-right: 10px;
}

.project-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.4;
  min-height: 20px;
}

.project-meta {
  margin-bottom: 15px;
}

.project-date {
  font-size: 12px;
  color: #909399;
}
</style>