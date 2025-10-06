import sqlite3
import json
from typing import List, Optional, Dict, Any
from app.database import get_db_connection
from app.models import User, Project, VideoFile

# 在文件内定义密码工具函数，避免循环导入
def get_password_hash(password: str) -> str:
    """密码加密"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

class SystemOperations:
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """获取系统统计信息"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户数量
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']

        # 获取项目数量
        cursor.execute("SELECT COUNT(*) as count FROM projects")
        projects_count = cursor.fetchone()['count']

        # 获取视频文件总数
        cursor.execute("SELECT COUNT(*) as count FROM project_videos")
        videos_count = cursor.fetchone()['count']

        # 获取总存储大小
        cursor.execute("SELECT SUM(file_size) as total_size FROM project_videos")
        total_size_result = cursor.fetchone()
        total_size = total_size_result['total_size'] or 0

        conn.close()

        return {
            "users_count": users_count,
            "projects_count": projects_count,
            "videos_count": videos_count,
            "total_size": total_size
        }


class BatchOperations:
    @staticmethod
    def get_project_videos_for_batch(project_id: int) -> List[Dict[str, Any]]:
        """获取项目的视频列表用于批量处理"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT filename, file_path FROM project_videos WHERE project_id = ?",
            (project_id,)
        )
        videos_data = cursor.fetchall()

        videos = []
        for video_data in videos_data:
            videos.append({
                "filename": video_data['filename'],
                "file_path": video_data['file_path']
            })

        conn.close()
        return videos

    @staticmethod
    def update_project_timestamp(project_id: int):
        """更新项目时间戳"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (project_id,)
        )
        conn.commit()
        conn.close()


class UserOperations:
    @staticmethod
    def create_user(username: str, email: str, password: str) -> Optional[User]:
        """创建用户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            password_hash = get_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()

            cursor.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,))
            user_data = cursor.fetchone()

            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    created_at=user_data['created_at']
                )
            return None

        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                raise ValueError("用户名已存在")
            elif "email" in str(e):
                raise ValueError("邮箱已存在")
            else:
                raise ValueError("用户创建失败")
        finally:
            conn.close()

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                created_at=user_data['created_at']
            )
        return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                created_at=user_data['created_at']
            )
        return None

    @staticmethod
    def verify_user_credentials(username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = UserOperations.get_user_by_username(username)
        if not user:
            return None

        if verify_password(password, user.password_hash):
            return user
        return None


class ProjectOperations:
    @staticmethod
    def create_project(user_id: int, title: str, description: str = "") -> Optional[Project]:
        """创建项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO projects (user_id, title, description) VALUES (?, ?, ?)",
                (user_id, title, description)
            )
            conn.commit()

            cursor.execute("SELECT * FROM projects WHERE id = ?", (cursor.lastrowid,))
            project_data = cursor.fetchone()

            if project_data:
                timeline_data = json.loads(project_data['timeline_data']) if project_data['timeline_data'] else {}
                return Project(
                    id=project_data['id'],
                    user_id=project_data['user_id'],
                    title=project_data['title'],
                    description=project_data['description'],
                    timeline_data=timeline_data,
                    created_at=project_data['created_at'],
                    updated_at=project_data['updated_at']
                )
            return None

        finally:
            conn.close()

    @staticmethod
    def get_user_projects(user_id: int) -> List[Project]:
        """获取用户的所有项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,)
        )
        projects_data = cursor.fetchall()

        projects = []
        for project_data in projects_data:
            timeline_data = json.loads(project_data['timeline_data']) if project_data['timeline_data'] else {}
            projects.append(Project(
                id=project_data['id'],
                user_id=project_data['user_id'],
                title=project_data['title'],
                description=project_data['description'],
                timeline_data=timeline_data,
                created_at=project_data['created_at'],
                updated_at=project_data['updated_at']
            ))

        conn.close()
        return projects

    @staticmethod
    def get_project(project_id: int) -> Optional[Project]:
        """根据ID获取项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project_data = cursor.fetchone()

        if project_data:
            timeline_data = json.loads(project_data['timeline_data']) if project_data['timeline_data'] else {}
            project = Project(
                id=project_data['id'],
                user_id=project_data['user_id'],
                title=project_data['title'],
                description=project_data['description'],
                timeline_data=timeline_data,
                created_at=project_data['created_at'],
                updated_at=project_data['updated_at']
            )
            conn.close()
            return project
        conn.close()
        return None


class VideoOperations:
    @staticmethod
    def add_video_to_project(project_id: int, filename: str, file_path: str,
                             duration: float, file_size: int, video_info: Dict) -> Optional[VideoFile]:
        """添加视频到项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO project_videos 
                (project_id, filename, file_path, duration, file_size, video_info) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (project_id, filename, file_path, duration, file_size, json.dumps(video_info))
            )

            cursor.execute(
                "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (project_id,)
            )

            conn.commit()

            cursor.execute("SELECT * FROM project_videos WHERE id = ?", (cursor.lastrowid,))
            video_data = cursor.fetchone()

            if video_data:
                video_info_data = json.loads(video_data['video_info']) if video_data['video_info'] else {}
                return VideoFile(
                    id=video_data['id'],
                    project_id=video_data['project_id'],
                    filename=video_data['filename'],
                    file_path=video_data['file_path'],
                    duration=video_data['duration'],
                    file_size=video_data['file_size'],
                    video_info=video_info_data,
                    added_at=video_data['added_at']
                )
            return None

        finally:
            conn.close()

    @staticmethod
    def get_project_videos(project_id: int) -> List[VideoFile]:
        """获取项目的所有视频"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM project_videos WHERE project_id = ? ORDER BY added_at DESC",
            (project_id,)
        )
        videos_data = cursor.fetchall()

        videos = []
        for video_data in videos_data:
            video_info = json.loads(video_data['video_info']) if video_data['video_info'] else {}
            videos.append(VideoFile(
                id=video_data['id'],
                project_id=video_data['project_id'],
                filename=video_data['filename'],
                file_path=video_data['file_path'],
                duration=video_data['duration'],
                file_size=video_data['file_size'],
                video_info=video_info,
                added_at=video_data['added_at']
            ))

        conn.close()
        return videos

    @staticmethod
    def add_processed_video_to_project(project_id: int, filename: str, file_path: str,
                                       operation_type: str, original_file: str):
        """添加处理后的视频到项目"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            from pathlib import Path
            import subprocess
            import json
            from datetime import datetime

            # 获取文件信息
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return None

            file_size = file_path_obj.stat().st_size

            # 获取视频时长
            duration = 0
            try:
                cmd = [
                    'ffprobe', '-v', 'error', '-show_format',
                    '-print_format', 'json', str(file_path)
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    video_info = json.loads(result.stdout)
                    duration = float(video_info['format'].get('duration', 0))
            except Exception as e:
                print(f"获取视频时长失败: {e}")
                # 如果获取时长失败，使用0

            # 构建视频信息
            video_info = {
                "operation": operation_type,
                "original_file": original_file,
                "processed_at": datetime.now().isoformat(),
                "file_size": file_size,
                "duration": duration
            }

            cursor.execute(
                """INSERT INTO project_videos 
                (project_id, filename, file_path, duration, file_size, video_info) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (project_id, filename, str(file_path), duration, file_size, json.dumps(video_info))
            )

            # 更新项目的更新时间
            cursor.execute(
                "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (project_id,)
            )

            conn.commit()

            # 获取刚添加的视频
            cursor.execute("SELECT * FROM project_videos WHERE id = ?", (cursor.lastrowid,))
            video_data = cursor.fetchone()

            if video_data:
                video_info_data = json.loads(video_data['video_info']) if video_data['video_info'] else {}
                return VideoFile(
                    id=video_data['id'],
                    project_id=video_data['project_id'],
                    filename=video_data['filename'],
                    file_path=video_data['file_path'],
                    duration=video_data['duration'],
                    file_size=video_data['file_size'],
                    video_info=video_info_data,
                    added_at=video_data['added_at']
                )
            return None

        except Exception as e:
            print(f"添加处理视频到项目失败: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

