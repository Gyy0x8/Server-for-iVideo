<template>
  <div class="video-uploader">
    <el-upload
      class="upload-demo"
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleFileChange"
      :show-file-list="false"
      :disabled="uploading"
    >
      <div class="upload-area" :class="{ 'is-dragover': isDragover }">
        <div class="upload-icon">📤</div>
        <div class="upload-text">
          <p class="upload-title">将视频文件拖到此处，或<em>点击选择</em></p>
          <p class="upload-hint">支持 MP4、MOV、AVI 等格式，文件大小不超过 500MB</p>
        </div>
      </div>
    </el-upload>

    <!-- 文件信息 -->
    <div v-if="selectedFile" class="file-info">
      <div class="file-details">
        <div class="file-icon">🎬</div>
        <div class="file-meta">
          <div class="file-name">{{ selectedFile.name }}</div>
          <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
        </div>
        <el-button 
          type="danger" 
          size="small" 
          text 
          @click="clearFile"
          :disabled="uploading"
        >
          移除
        </el-button>
      </div>

      <el-button
        type="primary"
        :loading="uploading"
        @click="handleUpload"
        class="upload-button"
      >
        {{ uploading ? '上传中...' : '开始上传' }}
      </el-button>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <el-progress 
        :percentage="uploadProgress" 
        :status="uploadError ? 'exception' : undefined"
        :show-text="false"
      />
      <div class="progress-text">
        {{ uploadError ? '上传失败' : `上传中... ${uploadProgress}%` }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/client'

export default {
  name: 'VideoUploader',
  props: {
    projectId: {
      type: Number,
      required: true
    }
  },
  emits: ['upload-success'],
  setup(props, { emit }) {
    const selectedFile = ref(null)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadError = ref(false)
    const isDragover = ref(false)

    const handleFileChange = (file) => {
      // 验证文件类型
      const allowedTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm']
      if (!allowedTypes.includes(file.raw.type)) {
        ElMessage.error('请选择视频文件（MP4、MOV、AVI、WebM格式）')
        return
      }

      // 验证文件大小
      const maxSize = 500 * 1024 * 1024
      if (file.raw.size > maxSize) {
        ElMessage.error('文件大小不能超过500MB')
        return
      }

      selectedFile.value = file.raw
      uploadError.value = false
      uploadProgress.value = 0
    }

    const handleUpload = async () => {
      if (!selectedFile.value) {
        ElMessage.warning('请先选择文件')
        return
      }

      try {
        uploading.value = true
        uploadError.value = false
        
        // 模拟上传进度
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 90) {
            uploadProgress.value += 10
          }
        }, 200)

        // 调用上传API
        const response = await api.uploadVideo(selectedFile.value)
        
        clearInterval(progressInterval)
        uploadProgress.value = 100

        // 将视频添加到项目
        await api.addVideoToProject(props.projectId, response.filename)

        ElMessage.success('视频上传成功！')
        
        // 重置状态
        selectedFile.value = null
        uploadProgress.value = 0
        
        // 通知父组件
        emit('upload-success')
        
      } catch (error) {
        console.error('Upload error:', error)
        uploadError.value = true
        ElMessage.error('上传失败，请重试')
      } finally {
        uploading.value = false
      }
    }

    const clearFile = () => {
      selectedFile.value = null
      uploadProgress.value = 0
      uploadError.value = false
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    return {
      selectedFile,
      uploading,
      uploadProgress,
      uploadError,
      isDragover,
      handleFileChange,
      handleUpload,
      clearFile,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.video-uploader {
  padding: 20px;
}

.upload-demo {
  width: 100%;
}

.upload-area {
  padding: 40px 20px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-area:hover,
.upload-area.is-dragover {
  border-color: #409EFF;
  background: #f0f7ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-title {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
}

.upload-title em {
  color: #409EFF;
  font-style: normal;
}

.upload-hint {
  font-size: 14px;
  color: #909399;
}

.file-info {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  background: #f9f9f9;
}

.file-details {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.file-icon {
  font-size: 32px;
  margin-right: 12px;
}

.file-meta {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.upload-button {
  width: 100%;
}

.upload-progress {
  margin-top: 16px;
}

.progress-text {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}
</style>