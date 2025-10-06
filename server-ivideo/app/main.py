from fastapi import FastAPI, UploadFile, File, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import shutil
import os
import subprocess
import json
from datetime import timedelta
from sqlalchemy.orm import Session
from starlette import status
from app.models import User, Project, VideoFile
from app.database import init_database, get_db_connection
from app.db_operations import UserOperations, ProjectOperations, VideoOperations,SystemOperations, BatchOperations
from typing import Optional, List
import uuid
from typing import Dict, Any
import urllib.parse
from app.auth import create_access_token, SECRET_KEY, ALGORITHM, decode_token
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas import UserCreate, UserLogin, Token, UserResponse

# 创建FastAPI应用
app = FastAPI(
    title="iVideo Server",
    description="VLog制作工具后端API",
    version="1.0.0"
)

# 创建上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# JWT配置
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

security = HTTPBearer()

def authenticate_user(username: str, password: str):

    return UserOperations.verify_user_credentials(username, password)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = UserOperations.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


# 允许所有跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():

    try:
        init_database()
        print("✅ 数据库初始化完成")

        # 验证表是否创建成功
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()

        table_names = [table['name'] for table in tables]
        print(f"📊 数据库表: {table_names}")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")

@app.get("/")
async def root():
    return {
        "message": "🎉 iVideo Server 启动成功！",
        "status": "running",
        "platform": os.name
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "iVideo Server"}

@app.post("/api/auth/register")
async def register_user(username: str, email: str, password: str):

    try:
        user = UserOperations.create_user(username, email, password)
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at
            }
        else:
            raise HTTPException(status_code=500, detail="用户创建失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 添加登录接口
@app.post("/api/auth/login")
async def login(username: str, password: str):

    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user.to_dict_without_password()
    }


# 添加获取当前用户信息接口
@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):

    return current_user.to_dict_without_password()

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):

    # 只能获取自己的用户信息
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权访问其他用户信息")

    user = UserOperations.get_user(user_id)
    if user:
        return user.to_dict_without_password()
    else:
        raise HTTPException(status_code=404, detail="用户不存在")

@app.post("/api/projects/create")
async def create_project(
    title: str,
    description: str = "",
    current_user: User = Depends(get_current_user)
):

    project = ProjectOperations.create_project(current_user.id, title, description)
    if project:
        return {
            "message": "项目创建成功",
            "project_id": project.id,
            "title": project.title,
            "created_at": project.created_at
        }
    else:
        raise HTTPException(status_code=500, detail="项目创建失败")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, current_user: User = Depends(get_current_user)):

    from app.db_operations import VideoOperations

    project = ProjectOperations.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 验证项目权限
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此项目")

    # 获取项目的视频文件
    videos = VideoOperations.get_project_videos(project_id)

    return {
        "project_id": project.id,
        "title": project.title,
        "description": project.description,
        "video_files": [video.to_dict() for video in videos],
        "audio_files": [],  # 后续可添加音频功能
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }

@app.get("/api/users/{user_id}/projects")
async def get_user_projects(user_id: int, current_user: User = Depends(get_current_user)):

    # 只能获取自己的项目
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="无权访问其他用户的项目")

    projects = ProjectOperations.get_user_projects(user_id)
    return {
        "user_id": user_id,
        "projects": [project.to_dict() for project in projects],
        "total_projects": len(projects)
    }

@app.post("/api/projects/{project_id}/add-video")
async def add_video_to_project(
        project_id: int,
        filename: str,
        current_user: User = Depends(get_current_user)
):

    # 验证项目权限
    project = ProjectOperations.get_project(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    # URL解码
    try:
        decoded_filename = urllib.parse.unquote(filename)
    except:
        decoded_filename = filename

    file_path = UPLOAD_DIR / decoded_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"视频文件不存在: {decoded_filename}")

    try:
        # 获取视频信息
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_format',
            '-show_streams',
            '-print_format', 'json',
            str(file_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0 or not result.stdout:
            raise HTTPException(status_code=500, detail="无法解析视频文件")

        video_info = json.loads(result.stdout)
        format_info = video_info.get('format', {})

        duration = float(format_info.get('duration', 0))
        file_size = int(format_info.get('size', 0))


        video_file = VideoOperations.add_video_to_project(
            project_id, decoded_filename, str(file_path),
            duration, file_size, video_info
        )

        if video_file:
            return {
                "message": "视频添加到项目成功",
                "project_id": project_id,
                "video_file": video_file.to_dict()
            }
        else:
            raise HTTPException(status_code=500, detail="视频添加失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频信息失败: {str(e)}")

@app.get("/api/projects/{project_id}/videos")
async def get_project_videos(project_id: int, current_user: User = Depends(get_current_user)):

    # 验证项目权限
    project = ProjectOperations.get_project(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    videos = VideoOperations.get_project_videos(project_id)
    return {
        "project_id": project_id,
        "videos": [video.to_dict() for video in videos],
        "total_videos": len(videos)
    }


@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...),current_user: User = Depends(get_current_user)):

    # 验证文件类型
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="只能上传视频文件")

    # 生成安全文件名
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
    file_path = UPLOAD_DIR / safe_filename

    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        return {
            "filename": safe_filename,
            "file_size": file_size,
            "message": "视频上传成功",
            "file_path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


# 挂载静态文件目录，方便访问上传的文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/api/video/info")
async def get_video_info(filename: str,current_user: User = Depends(get_current_user)):

    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    try:
        # 使用FFmpeg获取视频信息
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')


        if result.returncode != 0 or not result.stdout:
            raise HTTPException(status_code=500, detail="无法解析视频文件")


        try:
            video_info = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"JSON解析失败: {str(e)}")

        # 提取关键信息
        format_info = video_info.get('format', {})
        streams = video_info.get('streams', [])


        video_stream = next((s for s in streams if s.get('codec_type') == 'video'), {})
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), {})


        fps = 0
        if video_stream.get('r_frame_rate'):
            try:
                num, den = map(int, video_stream['r_frame_rate'].split('/'))
                fps = num / den if den != 0 else 0
            except (ValueError, ZeroDivisionError):
                fps = 0

        response_data = {
            "filename": filename,
            "format": format_info.get('format_name', 'unknown'),
            "duration": float(format_info.get('duration', 0)),
            "size": int(format_info.get('size', 0)),
            "bit_rate": int(format_info.get('bit_rate', 0)),
            "video": {
                "codec": video_stream.get('codec_name', 'unknown'),
                "width": video_stream.get('width', 0),
                "height": video_stream.get('height', 0),
                "fps": round(fps, 2),
                "bit_rate": video_stream.get('bit_rate', 'unknown'),
                "profile": video_stream.get('profile', 'unknown')
            } if video_stream else None,
            "audio": {
                "codec": audio_stream.get('codec_name', 'unknown'),
                "channels": audio_stream.get('channels', 0),
                "sample_rate": audio_stream.get('sample_rate', 'unknown'),
                "bit_rate": audio_stream.get('bit_rate', 'unknown')
            } if audio_stream else None
        }

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频信息失败: {str(e)}")


@app.post("/api/video/clip")
async def clip_video(
        filename: str,
        start_time: float,
        end_time: float,
        project_id: int,
        current_user: User = Depends(get_current_user)
):

    # 验证项目权限
    project = ProjectOperations.get_project(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    input_path = UPLOAD_DIR / filename
    output_filename = f"clip_{start_time}_{end_time}_{filename}"
    output_path = UPLOAD_DIR / output_filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    try:
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-ss', str(start_time),
            '-to', str(end_time),
            '-c', 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            # 自动添加到项目
            video_file = VideoOperations.add_processed_video_to_project(
                project_id=project_id,
                filename=output_filename,
                file_path=str(output_path),
                operation_type="clip",
                original_file=filename
            )

            return {
                "message": "视频剪辑成功",
                "original_file": filename,
                "clipped_file": output_filename,
                "output_path": str(output_path),
                "project_id": project_id,
                "added_to_project": video_file is not None,
                "video_id": video_file.id if video_file else None,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time
            }
        else:
            error_detail = result.stderr if result.stderr else "未知错误"
            raise HTTPException(status_code=500, detail=f"视频剪辑失败: {error_detail}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"剪辑处理失败: {str(e)}")


@app.post("/api/video/convert")
async def convert_video(
        filename: str,
        target_format: str = "mp4",
        quality: str = "medium",
        project_id: int = None,
        current_user: User = Depends(get_current_user)
):

    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    # 验证项目权限
    if project_id:
        project = ProjectOperations.get_project(project_id)
        if not project or project.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    # 支持的格式和质量映射
    format_settings = {
        "mp4": {"codec": "libx264", "extension": "mp4"},
        "webm": {"codec": "libvpx", "extension": "webm"},
        "avi": {"codec": "mpeg4", "extension": "avi"},
        "gif": {"codec": "gif", "extension": "gif"}
    }

    if target_format not in format_settings:
        raise HTTPException(status_code=400, detail=f"不支持的目标格式: {target_format}")

    output_filename = f"converted_{filename.rsplit('.', 1)[0]}.{format_settings[target_format]['extension']}"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 构建FFmpeg命令
        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-c:v', format_settings[target_format]['codec'],
            '-y'
        ]

        # 添加质量设置
        if quality == "high" and target_format == "mp4":
            cmd.extend(['-crf', '18'])
        elif quality == "low" and target_format == "mp4":
            cmd.extend(['-crf', '28'])

        # 对于GIF，需要特殊处理
        if target_format == "gif":
            cmd.extend(['-vf', 'fps=10,scale=480:-1:flags=lanczos'])

        cmd.append(str(output_path))

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            # 如果提供了project_id，自动添加到项目
            video_file = None
            if project_id:
                video_file = VideoOperations.add_processed_video_to_project(
                    project_id=project_id,
                    filename=output_filename,
                    file_path=str(output_path),
                    operation_type=f"convert_{target_format}",
                    original_file=filename
                )

            return {
                "message": "视频转换成功",
                "original_file": filename,
                "converted_file": output_filename,
                "output_path": str(output_path),
                "project_id": project_id,
                "added_to_project": video_file is not None,
                "video_id": video_file.id if video_file else None,
                "target_format": target_format,
                "quality": quality
            }
        else:
            error_detail = result.stderr if result.stderr else "未知错误"
            raise HTTPException(status_code=500, detail=f"视频转换失败: {error_detail}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换处理失败: {str(e)}")


@app.post("/api/video/filter")
async def apply_video_filter(
        filename: str,
        filter_type: str = "brightness",
        intensity: float = 0.1,
        project_id: int = None,
        current_user: User = Depends(get_current_user)
):

    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    # 验证项目权限
    if project_id:
        project = ProjectOperations.get_project(project_id)
        if not project or project.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    # 滤镜映射
    filters = {
        "brightness": f"eq=brightness={intensity}",
        "contrast": f"eq=contrast={1.0 + intensity}",
        "saturation": f"eq=saturation={1.0 + intensity}",
        "vignette": f"vignette=angle=PI/4:factor={intensity}",
        "sharpen": f"unsharp=5:5:{intensity}"
    }

    if filter_type not in filters:
        raise HTTPException(status_code=400, detail=f"不支持的滤镜类型: {filter_type}")

    output_filename = f"filtered_{filter_type}_{filename}"
    output_path = UPLOAD_DIR / output_filename

    try:
        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', filters[filter_type],
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            # 如果提供了project_id，自动添加到项目
            video_file = None
            if project_id:
                video_file = VideoOperations.add_processed_video_to_project(
                    project_id=project_id,
                    filename=output_filename,
                    file_path=str(output_path),
                    operation_type=f"filter_{filter_type}",
                    original_file=filename
                )

            return {
                "message": "滤镜应用成功",
                "original_file": filename,
                "filtered_file": output_filename,
                "output_path": str(output_path),
                "project_id": project_id,
                "added_to_project": video_file is not None,
                "video_id": video_file.id if video_file else None,
                "filter_type": filter_type,
                "intensity": intensity
            }
        else:
            error_detail = result.stderr if result.stderr else "未知错误"
            raise HTTPException(status_code=500, detail=f"滤镜应用失败: {error_detail}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"滤镜处理失败: {str(e)}")


@app.post("/api/video/watermark")
async def add_watermark(
        filename: str,
        watermark_text: str = "iVideo",
        position: str = "bottom-right",
        project_id: int = None,
        current_user: User = Depends(get_current_user)
):

    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    # 验证项目权限
    if project_id:
        project = ProjectOperations.get_project(project_id)
        if not project or project.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    # 位置映射
    positions = {
        "top-left": "10:10",
        "top-right": "main_w-text_w-10:10",
        "bottom-left": "10:main_h-text_h-10",
        "bottom-right": "main_w-text_w-10:main_h-text_h-10",
        "center": "(main_w-text_w)/2:(main_h-text_h)/2"
    }

    if position not in positions:
        raise HTTPException(status_code=400, detail=f"不支持的位置: {position}")

    output_filename = f"watermarked_{filename}"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 使用drawtext滤镜添加文字水印
        drawtext_filter = (
            f"drawtext=text='{watermark_text}':fontcolor=white:fontsize=24:"
            f"box=1:boxcolor=black@0.5:boxborderw=5:"
            f"x={positions[position].split(':')[0]}:y={positions[position].split(':')[1]}"
        )

        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', drawtext_filter,
            '-codec:a', 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            # 如果提供了project_id，自动添加到项目
            video_file = None
            if project_id:
                video_file = VideoOperations.add_processed_video_to_project(
                    project_id=project_id,
                    filename=output_filename,
                    file_path=str(output_path),
                    operation_type="watermark",
                    original_file=filename
                )

            return {
                "message": "水印添加成功",
                "original_file": filename,
                "watermarked_file": output_filename,
                "output_path": str(output_path),
                "project_id": project_id,
                "added_to_project": video_file is not None,
                "video_id": video_file.id if video_file else None,
                "watermark_text": watermark_text,
                "position": position
            }
        else:
            error_detail = result.stderr if result.stderr else "未知错误"
            raise HTTPException(status_code=500, detail=f"水印添加失败: {error_detail}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"水印处理失败: {str(e)}")


@app.post("/api/video/merge")
async def merge_videos(filenames: str, output_name: str = "merged_vlog",current_user: User = Depends(get_current_user)):

    file_list = [name.strip() for name in filenames.split(",")]

    # 验证所有文件存在
    missing_files = []
    for filename in file_list:
        if not (UPLOAD_DIR / filename).exists():
            missing_files.append(filename)

    if missing_files:
        raise HTTPException(status_code=404, detail=f"文件不存在: {', '.join(missing_files)}")

    # 创建文件列表
    list_file_path = UPLOAD_DIR / "merge_list.txt"
    with open(list_file_path, 'w', encoding='utf-8') as f:
        for filename in file_list:
            file_path = UPLOAD_DIR / filename
            # 使用绝对路径避免编码问题
            f.write(f"file '{file_path.absolute()}'\n")

    output_filename = f"{output_name}.mp4"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 使用 concat demuxer 合并视频
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file_path),
            '-c', 'copy',  # 流复制，快速合并
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        # 清理临时文件
        list_file_path.unlink(missing_ok=True)

        if result.returncode == 0:
            return {
                "message": "视频合并成功",
                "merged_files": file_list,
                "output_file": output_filename,
                "output_path": str(output_path)
            }
        else:
            raise HTTPException(status_code=500, detail=f"视频合并失败: {result.stderr}")

    except Exception as e:
        # 确保清理临时文件
        list_file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"合并处理失败: {str(e)}")


@app.post("/api/video/extract-audio")
async def extract_audio(filename: str, audio_format: str = "mp3",current_user: User = Depends(get_current_user)):
    """从视频中提取音频"""
    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    supported_formats = ["mp3", "aac", "wav", "m4a"]
    if audio_format not in supported_formats:
        raise HTTPException(status_code=400, detail=f"不支持的音频格式: {audio_format}")

    output_filename = f"{filename.rsplit('.', 1)[0]}.{audio_format}"
    output_path = UPLOAD_DIR / output_filename

    try:
        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vn',  # 忽略视频流
            '-acodec', 'libmp3lame' if audio_format == "mp3" else 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {
                "message": "音频提取成功",
                "video_file": filename,
                "audio_file": output_filename,
                "audio_format": audio_format
            }
        else:
            raise HTTPException(status_code=500, detail=f"音频提取失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频提取处理失败: {str(e)}")


@app.post("/api/video/replace-audio")
async def replace_audio(video_filename: str, audio_filename: str,current_user: User = Depends(get_current_user)):
    """为视频替换背景音乐"""
    video_path = UPLOAD_DIR / video_filename
    audio_path = UPLOAD_DIR / audio_filename

    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"视频文件不存在: {video_filename}")
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail=f"音频文件不存在: {audio_filename}")

    output_filename = f"with_bgm_{video_filename}"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 复制视频流，替换音频流
        cmd = [
            'ffmpeg',
            '-i', str(video_path),  # 输入视频
            '-i', str(audio_path),  # 输入音频
            '-c:v', 'copy',  # 视频流直接复制
            '-map', '0:v:0',  # 选择第一个输入的视频流
            '-map', '1:a:0',  # 选择第二个输入的音频流
            '-shortest',  # 以最短的流为准
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {
                "message": "音频替换成功",
                "video_file": video_filename,
                "audio_file": audio_filename,
                "output_file": output_filename
            }
        else:
            raise HTTPException(status_code=500, detail=f"音频替换失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音频替换处理失败: {str(e)}")


@app.post("/api/video/compress")
async def compress_video(
        filename: str,
        quality: str = "medium",
        target_size: int = None,
        current_user: User = Depends(get_current_user)
):
    """压缩视频文件"""
    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    output_filename = f"compressed_{filename}"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 基础命令
        cmd = ['ffmpeg', '-i', str(input_path)]

        # 根据质量设置参数
        if quality == "high":
            cmd.extend(['-crf', '23'])  # 高质量，较大文件
        elif quality == "medium":
            cmd.extend(['-crf', '28'])  # 中等质量
        elif quality == "low":
            cmd.extend(['-crf', '32'])  # 低质量，小文件

        # 如果指定目标大小，使用二次编码
        if target_size:
            # 获取原视频时长
            info_cmd = [
                'ffprobe', '-v', 'quiet', '-show_format',
                '-print_format', 'json', str(input_path)
            ]
            info_result = subprocess.run(info_cmd, capture_output=True, text=True)
            video_info = json.loads(info_result.stdout)
            duration = float(video_info['format']['duration'])

            # 计算目标比特率
            target_bitrate = int((target_size * 1024 * 8) / duration)
            cmd.extend(['-b:v', f'{target_bitrate}k'])

        cmd.extend([
            '-c:a', 'aac',  # 音频编码
            '-y',
            str(output_path)
        ])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # 获取压缩后文件大小
            compressed_size = output_path.stat().st_size
            original_size = input_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100

            return {
                "message": "视频压缩成功",
                "original_file": filename,
                "compressed_file": output_filename,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": round(compression_ratio, 2)
            }
        else:
            raise HTTPException(status_code=500, detail=f"视频压缩失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"压缩处理失败: {str(e)}")


@app.post("/api/video/add-subtitle")
async def add_subtitle(
        filename: str,
        subtitle_text: str,
        start_time: float,
        duration: float = 5.0,
        font_size: int = 24,
        font_color: str = "white",
        current_user: User = Depends(get_current_user)
):
    """为视频添加时间轴字幕"""
    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    output_filename = f"subtitle_{filename}"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 构建字幕滤镜
        subtitle_filter = (
            f"drawtext=text='{subtitle_text}':"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"box=1:boxcolor=black@0.5:boxborderw=5:"
            f"x=(w-text_w)/2:y=h-text_h-20:"  # 底部居中
            f"enable='between(t,{start_time},{start_time + duration})'"
        )

        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', subtitle_filter,
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {
                "message": "字幕添加成功",
                "video_file": filename,
                "output_file": output_filename,
                "subtitle_text": subtitle_text,
                "start_time": start_time,
                "duration": duration,
                "position": "bottom-center"
            }
        else:
            raise HTTPException(status_code=500, detail=f"字幕添加失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"字幕处理失败: {str(e)}")


@app.post("/api/video/add-multiple-subtitles")
async def add_multiple_subtitles(
        filename: str,
        subtitles: str,
        current_user: User = Depends(get_current_user)
):
    """批量添加多个字幕"""
    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    try:
        subtitle_list = json.loads(subtitles)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="字幕格式错误，应为JSON数组")

    output_filename = f"multisub_{filename}"
    output_path = UPLOAD_DIR / output_filename

    try:
        # 构建多个字幕的滤镜链
        subtitle_filters = []
        for i, sub in enumerate(subtitle_list):
            filter_str = (
                f"drawtext=text='{sub['text']}':"
                f"fontsize=24:fontcolor=white:"
                f"box=1:boxcolor=black@0.5:boxborderw=5:"
                f"x=(w-text_w)/2:y=h-text_h-20:"
                f"enable='between(t,{sub['start']},{sub['start'] + sub['duration']})'"
            )
            subtitle_filters.append(filter_str)

        # 连接所有滤镜
        filter_chain = ",".join(subtitle_filters)

        cmd = [
            'ffmpeg', '-i', str(input_path),
            '-vf', filter_chain,
            '-c:a', 'copy',
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {
                "message": "多字幕添加成功",
                "video_file": filename,
                "output_file": output_filename,
                "subtitle_count": len(subtitle_list),
                "subtitles": subtitle_list
            }
        else:
            raise HTTPException(status_code=500, detail=f"多字幕添加失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多字幕处理失败: {str(e)}")


@app.post("/api/video/to-gif")
async def video_to_gif(
        filename: str,
        start_time: float = 0,
        duration: float = 5.0,
        width: int = 480,
        current_user: User = Depends(get_current_user)
):
    """将视频片段转换为GIF"""
    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    output_filename = f"{filename.rsplit('.', 1)[0]}.gif"
    output_path = UPLOAD_DIR / output_filename

    try:
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),  # 开始时间
            '-t', str(duration),  # 持续时间
            '-i', str(input_path),
            '-vf', f"fps=10,scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",  # GIF优化
            '-loop', '0',  # 无限循环
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            gif_size = output_path.stat().st_size

            return {
                "message": "GIF转换成功",
                "video_file": filename,
                "gif_file": output_filename,
                "start_time": start_time,
                "duration": duration,
                "width": width,
                "file_size": gif_size,
                "usage": "适合社交媒体分享"
            }
        else:
            raise HTTPException(status_code=500, detail=f"GIF转换失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GIF处理失败: {str(e)}")


@app.post("/api/video/thumbnail")
async def generate_thumbnail(
        filename: str,
        time_point: float = 0,
        width: int = 320,
        current_user: User = Depends(get_current_user)
):
    """生成视频预览图"""
    input_path = UPLOAD_DIR / filename

    if not input_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")

    output_filename = f"thumbnail_{filename.rsplit('.', 1)[0]}.jpg"
    output_path = UPLOAD_DIR / output_filename

    try:
        cmd = [
            'ffmpeg',
            '-ss', str(time_point),  # 截图时间点
            '-i', str(input_path),
            '-vframes', '1',  # 只取一帧
            '-vf', f"scale={width}:-1",  # 缩放
            '-q:v', '2',  # 高质量
            '-y',
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            thumbnail_size = output_path.stat().st_size

            return {
                "message": "预览图生成成功",
                "video_file": filename,
                "thumbnail_file": output_filename,
                "time_point": time_point,
                "width": width,
                "file_size": thumbnail_size,
                "format": "JPEG"
            }
        else:
            raise HTTPException(status_code=500, detail=f"预览图生成失败: {result.stderr}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览图处理失败: {str(e)}")



@app.post("/api/projects/{project_id}/batch-process")
async def batch_process_project(
    project_id: int,
    operations: str,
    current_user: User = Depends(get_current_user)
):
    """批量处理项目中的所有视频"""
    from app.db_operations import BatchOperations

    # 验证项目权限
    project = ProjectOperations.get_project(project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="项目不存在或无权访问")

    try:
        operation_list = json.loads(operations)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="操作格式错误")

    # 获取项目的视频文件
    videos = BatchOperations.get_project_videos_for_batch(project_id)
    results = []

    for video_info in videos:
        filename = video_info["filename"]
        video_results = {"filename": filename, "operations": []}

        for operation in operation_list:
            try:
                if operation["type"] == "compress":
                    result = await compress_video_internal(filename, operation.get("quality", "medium"))
                    video_results["operations"].append({
                        "type": "compress",
                        "result": result
                    })

                elif operation["type"] == "add_watermark":
                    result = await add_watermark_internal(
                        filename,
                        operation.get("text", "iVideo"),
                        operation.get("position", "bottom-right")
                    )
                    video_results["operations"].append({
                        "type": "add_watermark",
                        "result": result
                    })

            except Exception as e:
                video_results["operations"].append({
                    "type": operation["type"],
                    "error": str(e)
                })

        results.append(video_results)

    # 更新项目时间戳
    BatchOperations.update_project_timestamp(project_id)

    return {
        "message": "批量处理完成",
        "project_id": project_id,
        "processed_files": len(results),
        "results": results
    }


# 内部处理函数
async def compress_video_internal(filename: str, quality: str):
    """内部压缩函数"""
    input_path = UPLOAD_DIR / filename
    output_filename = f"batch_compressed_{filename}"
    output_path = UPLOAD_DIR / output_filename

    cmd = [
        'ffmpeg', '-i', str(input_path),
        '-crf', '28' if quality == "medium" else '32',
        '-c:a', 'copy', '-y', str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return {"output_file": output_filename, "status": "success"}
    else:
        return {"status": "failed", "error": result.stderr}


async def add_watermark_internal(filename: str, text: str, position: str):
    """内部水印函数"""
    input_path = UPLOAD_DIR / filename
    output_filename = f"batch_watermark_{filename}"
    output_path = UPLOAD_DIR / output_filename

    positions = {
        "bottom-right": "main_w-text_w-10:main_h-text_h-10"
    }

    drawtext_filter = f"drawtext=text='{text}':fontcolor=white:fontsize=20:x={positions[position].split(':')[0]}:y={positions[position].split(':')[1]}"

    cmd = [
        'ffmpeg', '-i', str(input_path),
        '-vf', drawtext_filter,
        '-c:a', 'copy', '-y', str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return {"output_file": output_filename, "status": "success"}
    else:
        return {"status": "failed", "error": result.stderr}


@app.get("/api/system/status")
async def get_system_status():
    """获取系统状态"""
    from app.db_operations import SystemOperations

    # 获取数据库统计
    stats = SystemOperations.get_system_stats()

    # 统计上传目录文件
    upload_files = list(UPLOAD_DIR.glob("*"))
    video_files = [f for f in upload_files if f.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']]
    processed_files = [f for f in upload_files if
                       any(prefix in f.name for prefix in ['clip_', 'filtered_', 'converted_', 'watermarked_'])]

    # 计算目录大小
    total_size = sum(f.stat().st_size for f in upload_files if f.is_file())

    return {
        "system": "iVideo VLog制作服务器",
        "status": "running",
        "users_count": stats["users_count"],
        "projects_count": stats["projects_count"],
        "videos_count": stats["videos_count"],
        "storage": {
            "total_files": len(upload_files),
            "video_files": len(video_files),
            "processed_files": len(processed_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "database_size_mb": round(stats["total_size"] / (1024 * 1024), 2)
        },
        "features_available": [
            "视频上传", "信息解析", "剪辑", "格式转换", "滤镜",
            "水印", "合并", "音频处理", "压缩", "字幕",
            "GIF转换", "预览图", "用户管理", "项目管理", "批量处理"
        ]
    }


if __name__ == "__main__":
    print("🚀 启动 iVideo Server...")
    print("📚 API文档: http://localhost:8001/docs")

    # 应用启动时初始化数据库
    @app.on_event("startup")
    async def startup_event():
        """应用启动时初始化数据库"""
        init_database()
        print("✅ 数据库初始化完成")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )