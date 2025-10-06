import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8001',
  timeout: 30000
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API方法
export default {
  // 认证相关
  async login(username, password) {
    const response = await apiClient.post('/api/auth/login', null, {
      params: { username, password }
    })
    return response.data
  },

  async register(username, email, password) {
    const response = await apiClient.post('/api/auth/register', null, {
      params: { username, email, password }
    })
    return response.data
  },

  async getCurrentUser() {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },

  // 项目管理
  async createProject(title, description = '') {
    const response = await apiClient.post('/api/projects/create', null, {
      params: { title, description }
    })
    return response.data
  },

  async getUserProjects(userId) {
    const response = await apiClient.get(`/api/users/${userId}/projects`)
    return response.data
  },

  async getProject(projectId) {
    const response = await apiClient.get(`/api/projects/${projectId}`)
    return response.data
  },

  // 视频管理
  async addVideoToProject(projectId, filename) {
    const response = await apiClient.post(`/api/projects/${projectId}/add-video`, null, {
      params: { filename }
    })
    return response.data
  },

  async getProjectVideos(projectId) {
    const response = await apiClient.get(`/api/projects/${projectId}/videos`)
    return response.data
  },

  // 视频处理
  async clipVideo(filename, startTime, endTime, projectId) {
  const response = await apiClient.post('/api/video/clip', null, {
    params: { 
      filename, 
      start_time: startTime, 
      end_time: endTime,
      project_id: projectId  
    }
  })
  return response.data
},

  async convertVideo(filename, targetFormat, quality = 'medium') {
    const response = await apiClient.post('/api/video/convert', null, {
      params: { filename, target_format: targetFormat, quality }
    })
    return response.data
  },

  async applyFilter(filename, filterType, intensity = 0.1) {
    const response = await apiClient.post('/api/video/filter', null, {
      params: { filename, filter_type: filterType, intensity }
    })
    return response.data
  },

  async addWatermark(filename, watermarkText, position = 'bottom-right') {
    const response = await apiClient.post('/api/video/watermark', null, {
      params: { filename, watermark_text: watermarkText, position }
    })
    return response.data
  },

  async addSubtitle(filename, subtitleText, startTime, duration = 5) {
    const response = await apiClient.post('/api/video/add-subtitle', null, {
      params: { filename, subtitle_text: subtitleText, start_time: startTime, duration }
    })
    return response.data
  },

  async mergeVideos(filenames, outputName = 'merged_vlog') {
    const response = await apiClient.post('/api/video/merge', null, {
      params: { filenames: filenames.join(','), output_name: outputName }
    })
    return response.data
  },

  // 文件上传
  async uploadVideo(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/api/upload/video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  // 系统状态
  async getSystemStatus() {
    const response = await apiClient.get('/api/system/status')
    return response.data
  }
}