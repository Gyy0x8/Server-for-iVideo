# Server for iVideo - VLog视频制作工具说明文档

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-teal.svg)](https://fastapi.tiangolo.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.0+-orange.svg)](https://ffmpeg.org/)

一个功能完整的全栈VLog视频制作工具，支持在线视频编辑、特效处理、格式转换等专业功能。无需安装专业软件，在浏览器中即可完成高质量视频制作。

## 特性功能

### 视频处理引擎

- **剪辑处理**: 精确时间剪辑、视频合并、分割
- **格式转换**: MP4、WebM、GIF等多种格式
- **滤镜特效**: 亮度、对比度、饱和度、锐化、暗角
- **水印字幕**: 文字水印、时间轴字幕、位置自定义
- **音频处理**: 音频提取、背景音乐替换

###  用户系统

-  JWT身份认证
- 项目管理与权限控制
- 文件组织与版本管理
- 处理历史记录

### 用户体验

- 现代化响应式界面
- HTML5原生视频播放器
- 实时处理进度显示
- 移动端友好设计

##  快速开始

### 环境要求

- **Python 3.8+**
- **Node.js 16+**
- **FFmpeg 4.0+**
- **现代浏览器** (Chrome 90+, Firefox 88+, Safari 14+)

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/Gyy0x8/Server-for-iVideo.git
cd Server-for-iVideo
```

#### 2. 后端部署

```bash
# 进入后端目录
cd server-ivideo

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装FFmpeg (以Ubuntu为例)
sudo apt update && sudo apt install ffmpeg

# 启动后端服务
python -m app.main
```

后端服务将在 http://localhost:8001 启动

#### 3. 前端部署

```bash
# 新开终端，进入前端目录
cd ivideo-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 4. 开始使用

1. 访问 http://localhost:5173
2. 注册新用户账号
3. 创建第一个项目
4. 上传视频并开始编辑

## 项目结构

```
ivideo/
├── server-ivideo/          # 后端服务
│   ├── app/
│   │   ├── main.py         # FastAPI主应用
│   │   ├── database.py     # 数据库配置
│   │   ├── models.py       # 数据模型
│   │   ├── auth.py         # 认证模块
│   │   └── db_operations.py # 数据库操作
│   ├── uploads/            # 视频文件存储
│   └── requirements.txt    # Python依赖
└── ivideo-frontend/        # 前端应用
    ├── src/
    │   ├── components/     # Vue组件
    │   ├── views/          # 页面视图
    │   ├── stores/         # 状态管理
    │   ├── api/            # API客户端
    │   └── router/         # 路由配置
    └── package.json        # Node.js依赖
```

- ## 功能模块详解

  ### 1. 用户认证模块

  **功能描述**: 用户注册、登录和权限管理

  **核心功能**:

  - 用户注册（用户名、邮箱、密码）
  - JWT Token认证
  - 用户信息管理
  - 权限验证中间件

  **API端点**:

  - `POST /api/auth/register` - 用户注册
  - `POST /api/auth/login` - 用户登录
  - `GET /api/auth/me` - 获取当前用户信息

  ### 2. 项目管理模块

  **功能描述**: VLog项目管理

  **核心功能**:

  - 项目创建和编辑
  - 项目列表查询
  - 项目权限验证
  - 视频文件关联管理

  **API端点**:

  - `POST /api/projects/create` - 创建项目
  - `GET /api/users/{user_id}/projects` - 获取用户项目
  - `GET /api/projects/{project_id}` - 获取项目详情
  - `POST /api/projects/{project_id}/add-video` - 添加视频到项目

  ### 3. 视频处理模块

  **功能描述**: 核心视频处理功能

  #### 3.1 基础处理

  - **视频剪辑**: 时间轴精确剪辑
  - **格式转换**: MP4、WebM、GIF等格式转换
  - **视频压缩**: 质量可调的压缩算法

  #### 3.2 特效处理

  - **滤镜系统**: 亮度、对比度、饱和度、锐化、暗角
  - **水印添加**: 文字水印，支持多种位置
  - **字幕添加**: 时间轴字幕，支持批量添加

  #### 3.3 高级功能

  - **视频合并**: 多片段合成
  - **音频处理**: 音频提取和替换
  - **预览图生成**: 自动生成视频封面

  **API端点**:

  - `POST /api/video/clip` - 视频剪辑
  - `POST /api/video/convert` - 格式转换
  - `POST /api/video/filter` - 应用滤镜
  - `POST /api/video/watermark` - 添加水印
  - `POST /api/video/add-subtitle` - 添加字幕
  - `POST /api/video/merge` - 视频合并
  - `POST /api/video/extract-audio` - 音频提取
  - `POST /api/video/replace-audio` - 音频替换
  - `POST /api/video/compress` - 视频压缩
  - `POST /api/video/to-gif` - 转GIF动画
  - `POST /api/video/thumbnail` - 生成预览图

  ### 4. 文件管理模块

  **功能描述**: 视频文件上传和管理

  **核心功能**:

  - 视频文件上传
  - 文件信息解析
  - 文件存储管理
  - 批量处理支持

  **API端点**:

  - `POST /api/upload/video` - 上传视频文件
  - `GET /api/projects/{project_id}/videos` - 获取项目视频列表

完整API文档：http://localhost:8001/docs

## 核心工具类

### 1. UserOperations (用户操作类)

**文件位置**: `app/db_operations.py`

**主要功能**:

- 用户注册和验证
- 用户信息查询
- 密码加密验证

**核心方法**:

python

```
# 创建用户
create_user(username, email, password)

# 用户认证
verify_user_credentials(username, password)

# 获取用户信息
get_user(user_id)
get_user_by_username(username)
```



### 2. ProjectOperations (项目操作类)

**文件位置**: `app/db_operations.py`

**主要功能**:

- 项目管理
- 项目权限验证
- 项目时间线管理

**核心方法**:

python

```
# 创建项目
create_project(user_id, title, description)

# 获取用户项目
get_user_projects(user_id)

# 获取项目详情
get_project(project_id)
```



### 3. VideoOperations (视频操作类)

**文件位置**: `app/db_operations.py`

**主要功能**:

- 视频文件管理
- 视频信息处理
- 项目视频关联

**核心方法**:

python

```
# 添加视频到项目
add_video_to_project(project_id, filename, file_path, duration, file_size, video_info)

# 获取项目视频
get_project_videos(project_id)
```



## API配置

### 路由配置

**认证相关**:

- `/api/auth/*` - 用户认证接口

**项目管理**:

- `/api/projects/*` - 项目CRUD操作
- `/api/users/{id}/projects` - 用户项目查询

**视频处理**:

- `/api/video/*` - 视频处理功能
- `/api/upload/video` - 文件上传

**系统管理**:

- `/api/system/status` - 系统状态
- `/api/debug/*` - 调试接口

### 认证配置

- **认证方式**: JWT Bearer Token
- **Token有效期**: 7天
- **权限验证**: 自动中间件验证

## 视频处理引擎

### FFmpeg集成

**基础命令封装**:

python

```
# 视频剪辑
ffmpeg -i input.mp4 -ss start_time -to end_time -c copy output.mp4

# 格式转换  
ffmpeg -i input.mp4 -c:v libx264 output.webm

# 滤镜应用
ffmpeg -i input.mp4 -vf "eq=brightness=0.1" output.mp4

# 水印添加
ffmpeg -i input.mp4 -vf "drawtext=text='Watermark'" output.mp4
```



### 错误处理

- **编码处理**: UTF-8编码支持
- **错误捕获**: 完整的异常处理
- **进度反馈**: 处理状态实时反馈



## 前端集成

### Vue.js前端项目

**项目位置**: `ivideo-frontend/`

**核心功能**:

- 用户界面和交互
- 实时视频预览
- 处理进度显示
- 项目管理界面

**技术栈**:

- Vue 3 + Composition API
- Element Plus UI组件库
- Pinia状态管理
- Vue Router路由管理

## 开发环境配置

### 环境要求

- **Python**: 3.9+
- **FFmpeg**: 最新版本
- **依赖包**: 见 `requirements.txt`

##  故障排除

### 常见问题

**1. 上传失败**

- 检查文件格式支持 (MP4, MOV, AVI, WebM)
- 确认文件大小不超过500MB
- 检查上传目录权限

**2. 视频处理失败**

- 验证FFmpeg安装
- 检查视频文件完整性
- 查看后端错误日志

**3. 播放问题**

- 确认浏览器支持HTML5视频
- 检查视频编码格式
- 尝试刷新页面

### 获取日志

```bash
# 后端日志
tail -f server-ivideo/logs/app.log

# 前端调试
# 浏览器开发者工具 -> Console
```

## 扩展建议

### 短期优化

1. **性能优化**
   - 视频处理队列系统
   - 缓存机制优化
   - 并发处理支持
2. **功能完善**
   - 更多视频滤镜效果
   - 音频处理增强
   - 模板系统支持

### 长期规划

1. **云服务集成**
   - 云存储支持（AWS S3、阿里云OSS）
   - CDN加速分发
   - 分布式处理集群
2. **AI功能集成**
   - 智能视频剪辑
   - 人脸识别和跟踪
   - 自动字幕生成
   - 场景识别和分类
3. **多端支持**
   - 移动端APP
   - 桌面客户端
   - 浏览器插件
