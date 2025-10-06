<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>欢迎回来，{{ user?.username }}！</h1>
      <p>开始制作你的精彩VLog吧</p>
    </div>

    <!-- 系统状态卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon user-icon">👥</div>
            <div class="stat-info">
              <div class="stat-number">{{ systemStatus.users_count || 0 }}</div>
              <div class="stat-label">总用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon project-icon">📁</div>
            <div class="stat-info">
              <div class="stat-number">{{ systemStatus.projects_count || 0 }}</div>
              <div class="stat-label">总项目</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon video-icon">🎬</div>
            <div class="stat-info">
              <div class="stat-number">{{ systemStatus.videos_count || 0 }}</div>
              <div class="stat-label">总视频</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon storage-icon">💾</div>
            <div class="stat-info">
              <div class="stat-number">{{ systemStatus.storage?.total_size_mb || 0 }}</div>
              <div class="stat-label">存储(MB)</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="12">
        <el-card class="action-card">
          <template #header>
            <div class="card-header">
              <span>快速开始</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button 
              type="primary" 
              size="large" 
              @click="$router.push('/projects')"
              class="action-button"
            >
              📁 管理项目
            </el-button>
            <el-button 
              type="success" 
              size="large" 
              @click="$router.push('/editor')"
              class="action-button"
            >
              🎬 视频编辑
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="action-card">
          <template #header>
            <div class="card-header">
              <span>功能特性</span>
            </div>
          </template>
          <div class="features-list">
            <div 
              v-for="feature in systemStatus.features_available || []" 
              :key="feature"
              class="feature-item"
            >
              ✅ {{ feature }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'
import { ElMessage } from 'element-plus'

export default {
  name: 'DashboardView',
  setup() {
    const authStore = useAuthStore()
    const systemStatus = ref({})
    const loading = ref(false)

    const user = authStore.user

    const loadSystemStatus = async () => {
      try {
        loading.value = true
        const response = await api.getSystemStatus()
        systemStatus.value = response
      } catch (error) {
        console.error('Load system status error:', error)
        ElMessage.error('获取系统状态失败')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadSystemStatus()
    })

    return {
      user,
      systemStatus,
      loading
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 40px;
}

.dashboard-header h1 {
  color: #303133;
  font-size: 32px;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #909399;
  font-size: 16px;
}

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  font-size: 48px;
  margin-right: 20px;
}

.user-icon { color: #409EFF; }
.project-icon { color: #67C23A; }
.video-icon { color: #E6A23C; }
.storage-icon { color: #F56C6C; }

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  margin-top: 30px;
}

.action-card {
  border-radius: 12px;
  height: 200px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: 100%;
  justify-content: center;
}

.action-button {
  width: 100%;
  height: 60px;
  font-size: 16px;
  font-weight: 500;
}

.features-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  height: 100%;
}

.feature-item {
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 14px;
  color: #606266;
}
</style>