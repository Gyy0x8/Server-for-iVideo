<template>
  <div class="editor-container">
    <div class="editor-header">
      <h1>视频编辑器</h1>
      <p v-if="currentProject">项目: {{ currentProject.title }}</p>
      <p v-else>创建或选择项目开始编辑</p>
    </div>

    <el-row :gutter="20">
      
      <el-col :span="6">
        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <span>视频文件</span>
              <el-button type="primary" size="small" @click="showUploadDialog = true">
                上传视频
              </el-button>
            </div>
          </template>

          <div v-if="videos.length === 0" class="empty-videos">
            <div class="empty-icon">🎬</div>
            <p>暂无视频文件</p>
            <el-button type="primary" @click="showUploadDialog = true">
              上传第一个视频
            </el-button>
          </div>

          <div v-else class="video-list">
            <div
              v-for="video in videos"
              :key="video.id"
              :class="['video-item', { active: selectedVideo?.id === video.id }]"
              @click="selectVideo(video)"
            >
              <div class="video-thumbnail">
                🎥
              </div>
              <div class="video-info">
                <div class="video-name">{{ video.filename }}</div>
                <div class="video-details">
                  {{ formatDuration(video.duration) }} • {{ formatFileSize(video.file_size) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>

        
        <el-card class="sidebar-card project-selector">
          <template #header>
            <div class="card-header">
              <span>项目选择</span>
            </div>
          </template>
          
          <el-select
            v-model="selectedProjectId"
            placeholder="选择项目"
            style="width: 100%"
            @change="loadProjectData"
          >
            <el-option
              v-for="project in userProjects"
              :key="project.id"
              :label="project.title"
              :value="project.id"
            />
          </el-select>

          <div v-if="currentProject" class="project-info">
            <p><strong>描述:</strong> {{ currentProject.description || '暂无描述' }}</p>
            <p><strong>视频数量:</strong> {{ currentProject.video_files?.length || 0 }}</p>
            <p><strong>创建时间:</strong> {{ formatDate(currentProject.created_at) }}</p>
          </div>
        </el-card>
      </el-col>

      
    <el-col :span="18">
      <el-card class="editor-main-card">
        <template #header>
          <div class="card-header">
            <span>视频处理工具</span>
            <div class="header-actions">
              <el-button 
                v-if="selectedVideo" 
                type="success" 
                @click="showProcessingDialog = true"
              >
                🛠️ 处理视频
              </el-button>
              <el-button 
                v-if="selectedVideo" 
                type="info" 
                @click="downloadVideo"
                :disabled="!selectedVideo"
              >
                📥 下载视频
              </el-button>
            </div>
          </div>
        </template>

        <div v-if="!selectedVideo" class="no-video-selected">
          <div class="placeholder-icon">🎬</div>
          <h3>选择视频开始编辑</h3>
          <p>从左侧选择一个视频文件，然后使用处理工具进行编辑</p>
        </div>

        <div v-else class="video-preview-section">
          <div class="video-info-panel">
            <h3>当前视频: {{ selectedVideo.filename }}</h3>
            <div class="video-stats">
              <el-tag>时长: {{ formatDuration(selectedVideo.duration) }}</el-tag>
              <el-tag>大小: {{ formatFileSize(selectedVideo.file_size) }}</el-tag>
              <el-tag type="success">可用</el-tag>
              <el-button 
                type="primary" 
                size="small" 
                @click="refreshVideo"
                :loading="refreshing"
              >
                🔄 刷新
              </el-button>
            </div>
          </div>

          
          <div class="video-preview">
            <div class="video-player-container">
              <video
                ref="videoPlayer"
                :src="getVideoUrl(selectedVideo.filename)"
                controls
                preload="metadata"
                class="html5-video-player"
                @loadedmetadata="onVideoLoaded"
                @error="onVideoError"
              >
                您的浏览器不支持 HTML5 视频播放器。
              </video>
              
              
              <div class="player-controls">
                <div class="control-group">
                  <el-button 
                    size="small" 
                    @click="togglePlay"
                    :icon="isPlaying ? 'VideoPause' : 'VideoPlay'"
                  >
                    {{ isPlaying ? '暂停' : '播放' }}
                  </el-button>
                  <el-button 
                    size="small" 
                    @click="toggleMute"
                    :icon="isMuted ? 'Microphone' : 'Mute'"
                  >
                    {{ isMuted ? '取消静音' : '静音' }}
                  </el-button>
                  <el-slider
                    v-model="volume"
                    :min="0"
                    :max="100"
                    :step="1"
                    show-stops
                    style="width: 100px; margin: 0 10px;"
                    @input="onVolumeChange"
                  />
                </div>
                
                <div class="video-info">
                  <span class="current-time">{{ formatTime(currentTime) }}</span>
                  <span class="duration-separator">/</span>
                  <span class="total-duration">{{ formatTime(duration) }}</span>
                </div>
              </div>

              
              <div class="video-details">
                <div class="detail-item">
                  <span class="detail-label">分辨率:</span>
                  <span class="detail-value">{{ videoWidth }} × {{ videoHeight }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">格式:</span>
                  <span class="detail-value">{{ getFileExtension(selectedVideo.filename) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">文件路径:</span>
                  <span class="detail-value file-path">{{ selectedVideo.file_path }}</span>
                </div>
              </div>
            </div>
          </div>

          
          <div v-if="processedFiles.length > 0" class="processed-files">
            <h4>处理后的文件</h4>
            <div class="files-grid">
              <div
                v-for="file in processedFiles"
                :key="file.name"
                class="processed-file-item"
                @click="playProcessedFile(file.name)"
              >
                <div class="file-icon">🎬</div>
                <div class="file-info">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-size">{{ formatFileSize(file.size) }}</div>
                </div>
                <el-button 
                  size="small" 
                  type="primary" 
                  text 
                  @click.stop="downloadFile(file.name)"
                >
                  下载
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
    </el-row>

    
    <el-dialog
      v-model="showUploadDialog"
      title="上传视频"
      width="500px"
    >
      <VideoUploader 
        :project-id="selectedProjectId"
        @upload-success="handleUploadSuccess"
      />
    </el-dialog>

    
  <el-dialog
    v-model="showProcessingDialog"
    title="视频处理"
    width="600px"
    v-if="selectedVideo && selectedProjectId"
  >
    <VideoProcessor 
      :video="selectedVideo"
      :project-id="selectedProjectId"
      @process-complete="handleProcessComplete"
    />
</el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'
import VideoUploader from '@/components/VideoUploader.vue'
import VideoProcessor from '@/components/VideoProcessor.vue'

export default {
  name: 'VideoEditorView',
  components: {
    VideoUploader,
    VideoProcessor
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()
    
    
    const userProjects = ref([])
    const selectedProjectId = ref(null)
    const currentProject = ref(null)
    const videos = ref([])
    const selectedVideo = ref(null)
    const showUploadDialog = ref(false)
    const showProcessingDialog = ref(false)
    const refreshing = ref(false)

    
    const videoPlayer = ref(null)
    const isPlaying = ref(false)
    const isMuted = ref(false)
    const volume = ref(50)
    const currentTime = ref(0)
    const duration = ref(0)
    const videoWidth = ref(0)
    const videoHeight = ref(0)
    const processedFiles = ref([])

    
    const getVideoUrl = (filename) => {
      return `http://localhost:8001/uploads/${encodeURIComponent(filename)}`
    }

    
    const togglePlay = () => {
      if (!videoPlayer.value) return
      
      if (videoPlayer.value.paused) {
        videoPlayer.value.play()
        isPlaying.value = true
      } else {
        videoPlayer.value.pause()
        isPlaying.value = false
      }
    }

    const toggleMute = () => {
      if (!videoPlayer.value) return
      
      videoPlayer.value.muted = !videoPlayer.value.muted
      isMuted.value = videoPlayer.value.muted
    }

    const onVolumeChange = (value) => {
      if (!videoPlayer.value) return
      
      videoPlayer.value.volume = value / 100
      isMuted.value = value === 0
    }

    const onVideoLoaded = (event) => {
      const video = event.target
      duration.value = video.duration
      videoWidth.value = video.videoWidth
      videoHeight.value = video.videoHeight
      
      
      video.volume = volume.value / 100
    }

    const onVideoError = (event) => {
      console.error('视频加载错误:', event)
      ElMessage.error('视频加载失败，请检查文件是否存在')
    }

    
    const updateTime = () => {
      if (videoPlayer.value) {
        currentTime.value = videoPlayer.value.currentTime
      }
    }

    
    const formatTime = (seconds) => {
      if (!seconds || isNaN(seconds)) return '0:00'
      
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    
    const getFileExtension = (filename) => {
      return filename.split('.').pop()?.toUpperCase() || '未知'
    }

    
    const refreshVideo = async () => {
      if (!selectedProjectId.value) return
      
      try {
        refreshing.value = true
        await loadProjectData()
        ElMessage.success('视频列表已刷新')
      } catch (error) {
        console.error('Refresh error:', error)
        ElMessage.error('刷新失败')
      } finally {
        refreshing.value = false
      }
    }

    
    const downloadVideo = () => {
      if (!selectedVideo.value) return
      
      const url = getVideoUrl(selectedVideo.value.filename)
      const link = document.createElement('a')
      link.href = url
      link.download = selectedVideo.value.filename
      link.click()
    }

    
    const downloadFile = (filename) => {
      const url = getVideoUrl(filename)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
    }

    
    const playProcessedFile = (filename) => {
      
      const processedVideo = videos.value.find(v => v.filename === filename)
      if (processedVideo) {
        selectVideo(processedVideo)
      }
    }

    
    const loadProcessedFiles = () => {
      if (!videos.value.length) return
      
      
      processedFiles.value = videos.value.filter(video => 
        video.filename.includes('clip_') ||
        video.filename.includes('filtered_') ||
        video.filename.includes('converted_') ||
        video.filename.includes('watermarked_')
      )
    }

    
    watch(videos, () => {
      loadProcessedFiles()
    })

    watch(selectedVideo, (newVideo) => {
      if (newVideo && videoPlayer.value) {
        
        isPlaying.value = false
        currentTime.value = 0
        
        
        setTimeout(() => {
          if (videoPlayer.value) {
            videoPlayer.value.load()
          }
        }, 100)
      }
    })

    
    const loadUserProjects = async () => {
      try {
        const response = await api.getUserProjects(authStore.user.id)
        userProjects.value = response.projects
        
        if (route.params.projectId) {
          selectedProjectId.value = parseInt(route.params.projectId)
        } else if (userProjects.value.length > 0) {
          selectedProjectId.value = userProjects.value[0].id
        }
      } catch (error) {
        console.error('Load user projects error:', error)
        ElMessage.error('加载项目失败')
      }
    }

    const loadProjectData = async () => {
      if (!selectedProjectId.value) return
      
      try {
        const projectResponse = await api.getProject(selectedProjectId.value)
        currentProject.value = projectResponse
        
        const videosResponse = await api.getProjectVideos(selectedProjectId.value)
        videos.value = videosResponse.videos
        
        selectedVideo.value = null
      } catch (error) {
        console.error('Load project data error:', error)
        ElMessage.error('加载项目数据失败')
      }
    }

    const selectVideo = (video) => {
      selectedVideo.value = video
    }

    const handleUploadSuccess = () => {
      showUploadDialog.value = false
      loadProjectData()
      ElMessage.success('视频上传成功！')
    }

    const handleProcessComplete = () => {
      showProcessingDialog.value = false
      ElMessage.success('视频处理完成！')
      loadProjectData()
    }

    const formatDuration = (seconds) => {
      if (!seconds) return '0:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadUserProjects()
      
      
      setInterval(updateTime, 1000)
    })

    watch(selectedProjectId, (newVal) => {
      if (newVal) {
        loadProjectData()
      }
    })

    return {
      userProjects,
      selectedProjectId,
      currentProject,
      videos,
      selectedVideo,
      showUploadDialog,
      showProcessingDialog,
      refreshing,
      
      
      videoPlayer,
      isPlaying,
      isMuted,
      volume,
      currentTime,
      duration,
      videoWidth,
      videoHeight,
      processedFiles,
      
      getVideoUrl,
      togglePlay,
      toggleMute,
      onVolumeChange,
      onVideoLoaded,
      onVideoError,
      formatTime,
      getFileExtension,
      refreshVideo,
      downloadVideo,
      downloadFile,
      playProcessedFile,
      
      loadProjectData,
      selectVideo,
      handleUploadSuccess,
      handleProcessComplete,
      formatDuration,
      formatFileSize,
      formatDate
    }
  }
}
</script>

<style scoped>
.editor-container {
  max-width: 1400px;
  margin: 0 auto;
}

.editor-header {
  margin-bottom: 30px;
}

.editor-header h1 {
  color: #303133;
  font-size: 32px;
  margin-bottom: 8px;
}

.editor-header p {
  color: #909399;
  font-size: 16px;
}

.sidebar-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.empty-videos {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-videos .empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.video-list {
  max-height: 400px;
  overflow-y: auto;
}

.video-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.video-item:hover {
  border-color: #409EFF;
  background: #f5f7fa;
}

.video-item.active {
  border-color: #409EFF;
  background: #ecf5ff;
}

.video-thumbnail {
  font-size: 24px;
  margin-right: 12px;
}

.video-info {
  flex: 1;
}

.video-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.video-details {
  font-size: 12px;
  color: #909399;
}

.project-selector .project-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e6e6e6;
}

.project-info p {
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.editor-main-card {
  border-radius: 12px;
  min-height: 500px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.no-video-selected {
  text-align: center;
  padding: 80px 20px;
  color: #909399;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.video-preview-section {
  padding: 20px;
}

.video-info-panel {
  margin-bottom: 20px;
}

.video-info-panel h3 {
  margin-bottom: 12px;
  color: #303133;
}

.video-stats {
  display: flex;
  gap: 10px;
}

.video-preview {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  background: #000;
  margin-bottom: 20px;
}

.video-player-container {
  padding: 0;
}

.html5-video-player {
  width: 100%;
  height: 400px;
  background: #000;
  border-radius: 8px 8px 0 0;
}

.player-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-top: 1px solid #e6e6e6;
  border-radius: 0 0 8px 8px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.video-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
}

.current-time {
  font-weight: 500;
}

.duration-separator {
  color: #909399;
}

.total-duration {
  color: #909399;
}

.video-details {
  padding: 16px;
  background: #f9f9f9;
  border-top: 1px solid #e6e6e6;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 500;
  color: #303133;
  min-width: 80px;
}

.detail-value {
  color: #606266;
  flex: 1;
}

.file-path {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  word-break: break-all;
}

.processed-files {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  background: #f9f9f9;
}

.processed-files h4 {
  margin-bottom: 12px;
  color: #303133;
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.processed-file-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.processed-file-item:hover {
  border-color: #409EFF;
  background: #f0f7ff;
}

.file-icon {
  font-size: 24px;
  margin-right: 12px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .html5-video-player {
    height: 300px;
  }
  
  .player-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .control-group {
    justify-content: center;
  }
  
  .files-grid {
    grid-template-columns: 1fr;
  }
}

.preview-placeholder {
  text-align: center;
  color: #909399;
}

.preview-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.preview-hint {
  font-size: 12px;
  margin-top: 8px;
}
</style>