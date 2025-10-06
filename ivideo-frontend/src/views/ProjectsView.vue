<template>
  <div class="projects-container">
    <div class="projects-header">
      <h1>项目管理</h1>
      <p>创建和管理你的VLog项目</p>
    </div>

    
    <el-card class="create-project-card">
      <template #header>
        <div class="card-header">
          <span>创建新项目</span>
        </div>
      </template>
      <el-form :model="newProject" :rules="projectRules" ref="projectFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目名称" prop="title">
              <el-input
                v-model="newProject.title"
                placeholder="输入项目名称"
                size="large"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目描述">
              <el-input
                v-model="newProject.description"
                placeholder="项目描述（可选）"
                size="large"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="creatingProject"
                @click="handleCreateProject"
                class="create-button"
              >
                {{ creatingProject ? '创建中...' : '创建项目' }}
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    
    <el-card class="projects-list-card">
      <template #header>
        <div class="card-header">
          <span>我的项目 ({{ projects.length }})</span>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="projects.length === 0" class="empty-state">
        <div class="empty-icon">📁</div>
        <h3>还没有项目</h3>
        <p>创建一个新项目开始制作VLog吧！</p>
      </div>

      <div v-else class="projects-grid">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card"
          @click="openProject(project.id)"
        >
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
            <span class="project-date" v-if="project.updated_at !== project.created_at">
              更新: {{ formatDate(project.updated_at) }}
            </span>
          </div>

          <div class="project-actions">
            <el-button
              type="primary"
              size="small"
              @click.stop="openEditor(project.id)"
            >
              🎬 编辑
            </el-button>
            <el-button
              type="info"
              size="small"
              @click.stop="viewProject(project.id)"
            >
              👁️ 查看
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

export default {
  name: 'ProjectsView',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const projects = ref([])
    const loading = ref(false)
    const creatingProject = ref(false)
    const projectFormRef = ref(null)

    const newProject = ref({
      title: '',
      description: ''
    })

    const projectRules = {
      title: [
        { required: true, message: '请输入项目名称', trigger: 'blur' },
        { min: 2, max: 50, message: '项目名称长度在 2 到 50 个字符', trigger: 'blur' }
      ]
    }

    const loadProjects = async () => {
  try {
    loading.value = true
    
    const response = await api.getUserProjects(authStore.user.id)
    projects.value = response.projects
  } catch (error) {
    console.error('Load projects error:', error)
    ElMessage.error('加载项目失败')
  } finally {
    loading.value = false
  }
}

    const handleCreateProject = async () => {
  if (!projectFormRef.value) return
  
  try {
    const valid = await projectFormRef.value.validate()
    if (!valid) return
    
    creatingProject.value = true
    
    
    await api.createProject(
      newProject.value.title,
      newProject.value.description
    )
    
    ElMessage.success('项目创建成功！')
    
    
    newProject.value.title = ''
    newProject.value.description = ''
    projectFormRef.value.resetFields()
    
    
    await loadProjects()
    
  } catch (error) {
    console.error('Create project error:', error)
    ElMessage.error('创建项目失败')
  } finally {
    creatingProject.value = false
  }
}

    const openEditor = (projectId) => {
      router.push(`/editor/${projectId}`)
    }

    const viewProject = (projectId) => {
      
      router.push(`/editor/${projectId}`)
    }

    const openProject = (projectId) => {
      router.push(`/editor/${projectId}`)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadProjects()
    })

    return {
      projects,
      loading,
      creatingProject,
      newProject,
      projectFormRef,
      projectRules,
      handleCreateProject,
      openEditor,
      viewProject,
      openProject,
      formatDate
    }
  }
}
</script>

<style scoped>
.projects-container {
  max-width: 1200px;
  margin: 0 auto;
}

.projects-header {
  margin-bottom: 30px;
}

.projects-header h1 {
  color: #303133;
  font-size: 32px;
  margin-bottom: 8px;
}

.projects-header p {
  color: #909399;
  font-size: 16px;
}

.create-project-card {
  margin-bottom: 30px;
  border-radius: 12px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.create-button {
  width: 100%;
}

.projects-list-card {
  border-radius: 12px;
}

.loading-container {
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #606266;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px;
}

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
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 15px;
}

.project-date {
  font-size: 12px;
  color: #909399;
}

.project-actions {
  display: flex;
  gap: 8px;
}
</style>