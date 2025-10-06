from datetime import datetime
from typing import Dict, Any
import json


class User:
    def __init__(self, id: int, username: str, email: str, password_hash: str, created_at: str):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at
        }

    def to_dict_without_password(self) -> Dict[str, Any]:
        """返回不包含密码的用户信息"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at
        }


# Project 和 VideoFile 类保持不变
class Project:
    def __init__(self, id: int, user_id: int, title: str, description: str,
                 timeline_data: Dict, created_at: str, updated_at: str):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.timeline_data = timeline_data
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "timeline_data": self.timeline_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class VideoFile:
    def __init__(self, id: int, project_id: int, filename: str, file_path: str,
                 duration: float, file_size: int, video_info: Dict, added_at: str):
        self.id = id
        self.project_id = project_id
        self.filename = filename
        self.file_path = file_path
        self.duration = duration
        self.file_size = file_size
        self.video_info = video_info
        self.added_at = added_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "duration": self.duration,
            "file_size": self.file_size,
            "video_info": self.video_info,
            "added_at": self.added_at
        }