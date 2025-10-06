<template>
  <div class="video-processor">
    <div class="processor-header">
      <h3>视频处理工具</h3>
      <p>对选中的视频进行各种处理操作</p>
    </div>

    <el-tabs v-model="activeTab" class="processor-tabs">
      <!-- 基础剪辑 -->
      <el-tab-pane label="✂️ 剪辑" name="clip">
        <div class="tab-content">
          <el-form :model="clipForm" label-width="80px">
            <el-form-item label="开始时间">
              <el-input-number
                v-model="clipForm.startTime"
                :min="0"
                :max="videoDuration"
                :step="0.1"
                controls-position="right"
              />
              <span class="time-unit">秒</span>
            </el-form-item>
            <el-form-item label="结束时间">
              <el-input-number
                v-model="clipForm.endTime"
                :min="clipForm.startTime"
                :max="videoDuration"
                :step="0.1"
                controls-position="right"
              />
              <span class="time-unit">秒</span>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleClip"
                :loading="processing"
              >
                执行剪辑
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 格式转换 -->
      <el-tab-pane label="🔄 转换" name="convert">
        <div class="tab-content">
          <el-form :model="convertForm" label-width="80px">
            <el-form-item label="目标格式">
              <el-radio-group v-model="convertForm.targetFormat">
                <el-radio label="mp4">MP4</el-radio>
                <el-radio label="webm">WebM</el-radio>
                <el-radio label="gif">GIF</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="质量">
              <el-radio-group v-model="convertForm.quality">
                <el-radio label="high">高质量</el-radio>
                <el-radio label="medium">中等质量</el-radio>
                <el-radio label="low">低质量</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleConvert"
                :loading="processing"
              >
                开始转换
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 滤镜效果 -->
      <el-tab-pane label="🎨 滤镜" name="filter">
        <div class="tab-content">
          <el-form :model="filterForm" label-width="80px">
            <el-form-item label="滤镜类型">
              <el-select v-model="filterForm.filterType" placeholder="选择滤镜">
                <el-option label="亮度" value="brightness" />
                <el-option label="对比度" value="contrast" />
                <el-option label="饱和度" value="saturation" />
                <el-option label="锐化" value="sharpen" />
                <el-option label="暗角" value="vignette" />
              </el-select>
            </el-form-item>
            <el-form-item label="强度">
              <el-slider
                v-model="filterForm.intensity"
                :min="0"
                :max="1"
                :step="0.1"
                show-stops
              />
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleFilter"
                :loading="processing"
              >
                应用滤镜
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 水印 -->
      <el-tab-pane label="💧 水印" name="watermark">
        <div class="tab-content">
          <el-form :model="watermarkForm" label-width="80px">
            <el-form-item label="水印文字">
              <el-input 
                v-model="watermarkForm.text" 
                placeholder="输入水印文字"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="位置">
              <el-radio-group v-model="watermarkForm.position">
                <el-radio label="top-left">左上</el-radio>
                <el-radio label="top-right">右上</el-radio>
                <el-radio label="bottom-left">左下</el-radio>
                <el-radio label="bottom-right">右下</el-radio>
                <el-radio label="center">居中</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleWatermark"
                :loading="processing"
              >
                添加水印
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 处理状态 -->
    <div v-if="processing" class="processing-status">
      <el-alert
        title="视频处理中..."
        type="info"
        :closable="false"
        show-icon
      />
      <div class="progress-info">
        <el-progress :percentage="processProgress" :show-text="false" />
        <p>请稍候，处理完成后会自动刷新列表</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/client'

export default {
  name: 'VideoProcessor',
  props: {
  video: {
    type: Object,
    required: true
  },
  projectId: {  
    type: Number,
    required: true
  }
},
  emits: ['process-complete'],
  setup(props, { emit }) {
    const activeTab = ref('clip')
    const processing = ref(false)
    const processProgress = ref(0)

    // 剪辑表单
    const clipForm = reactive({
      startTime: 0,
      endTime: computed(() => Math.min(props.video.duration, 30)) 
    })

    // 转换表单
    const convertForm = reactive({
      targetFormat: 'mp4',
      quality: 'medium'
    })

    // 滤镜表单
    const filterForm = reactive({
      filterType: 'brightness',
      intensity: 0.1
    })

    // 水印表单
    const watermarkForm = reactive({
      text: 'iVideo',
      position: 'bottom-right'
    })

    const videoDuration = computed(() => props.video.duration || 0)

    const simulateProgress = () => {
      processProgress.value = 0
      const interval = setInterval(() => {
        if (processProgress.value < 90) {
          processProgress.value += 10
        } else {
          clearInterval(interval)
        }
      }, 500)
      return interval
    }

    const handleClip = async () => {
  if (clipForm.endTime <= clipForm.startTime) {
    ElMessage.error('结束时间必须大于开始时间')
    return
  }

  try {
    processing.value = true
    const progressInterval = simulateProgress()

    console.log('开始剪辑，项目ID:', props.projectId) 

    // 确保传递所有参数
    const response = await api.clipVideo(
      props.video.filename,
      clipForm.startTime,
      clipForm.endTime,
      props.projectId  
    )

    clearInterval(progressInterval)
    processProgress.value = 100
    
    if (response.added_to_project) {
      ElMessage.success('视频剪辑成功！已自动添加到项目')
    } else {
      ElMessage.success('视频剪辑成功！')
    }
    emit('process-complete', response)
  } catch (error) {
    console.error('Clip video error:', error)
    console.error('错误详情:', error.response?.data) 
    ElMessage.error('剪辑失败，请重试')
  } finally {
    processing.value = false
    processProgress.value = 0
  }
}

    const handleConvert = async () => {
  try {
    processing.value = true
    const progressInterval = simulateProgress()

    
    const response = await api.convertVideo(
      props.video.filename,
      convertForm.targetFormat,
      convertForm.quality,
      props.projectId  
    )

    clearInterval(progressInterval)
    processProgress.value = 100
    
    if (response.added_to_project) {
      ElMessage.success('视频转换成功！已自动添加到项目')
    } else {
      ElMessage.success('视频转换成功！')
    }
    emit('process-complete', response)
  } catch (error) {
    console.error('Convert video error:', error)
    ElMessage.error('转换失败，请重试')
  } finally {
    processing.value = false
    processProgress.value = 0
  }
}

    const handleFilter = async () => {
  try {
    processing.value = true
    const progressInterval = simulateProgress()

    
    const response = await api.applyFilter(
      props.video.filename,
      filterForm.filterType,
      filterForm.intensity,
      props.projectId  
    )

    clearInterval(progressInterval)
    processProgress.value = 100
    
    if (response.added_to_project) {
      ElMessage.success('滤镜应用成功！已自动添加到项目')
    } else {
      ElMessage.success('滤镜应用成功！')
    }
    emit('process-complete', response)
  } catch (error) {
    console.error('Apply filter error:', error)
    ElMessage.error('滤镜应用失败，请重试')
  } finally {
    processing.value = false
    processProgress.value = 0
  }
}

    const handleWatermark = async () => {
  if (!watermarkForm.text.trim()) {
    ElMessage.error('请输入水印文字')
    return
  }

  try {
    processing.value = true
    const progressInterval = simulateProgress()

    
    const response = await api.addWatermark(
      props.video.filename,
      watermarkForm.text,
      watermarkForm.position,
      props.projectId  
    )

    clearInterval(progressInterval)
    processProgress.value = 100
    
    if (response.added_to_project) {
      ElMessage.success('水印添加成功！已自动添加到项目')
    } else {
      ElMessage.success('水印添加成功！')
    }
    emit('process-complete', response)
  } catch (error) {
    console.error('Add watermark error:', error)
    ElMessage.error('水印添加失败，请重试')
  } finally {
    processing.value = false
    processProgress.value = 0
  }
}

    return {
      activeTab,
      processing,
      processProgress,
      clipForm,
      convertForm,
      filterForm,
      watermarkForm,
      videoDuration,
      handleClip,
      handleConvert,
      handleFilter,
      handleWatermark
    }
  }
}
</script>

<style scoped>
.video-processor {
  padding: 0 10px;
}

.processor-header {
  margin-bottom: 20px;
  text-align: center;
}

.processor-header h3 {
  color: #303133;
  margin-bottom: 8px;
}

.processor-header p {
  color: #909399;
  font-size: 14px;
}

.processor-tabs {
  margin-bottom: 20px;
}

.tab-content {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.time-unit {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}

.processing-status {
  margin-top: 20px;
}

.progress-info {
  margin-top: 16px;
  text-align: center;
}

.progress-info p {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
</style>