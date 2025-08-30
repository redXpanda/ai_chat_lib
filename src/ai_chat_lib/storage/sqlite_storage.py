"""
SQLite存储实现（接口预留）
"""
from typing import List, Optional
from .base import BaseStorage
from ..models.character import Character

class SQLiteStorage(BaseStorage):
    """SQLite数据库存储实现（预留接口）"""
    
    def __init__(self, db_path: str = "characters.db"):
        self.db_path = db_path
        # TODO: 初始化数据库连接和表结构
        
    def load_character(self, name: str) -> Optional[Character]:
        """从数据库加载角色"""
        # TODO: 实现数据库查询
        raise NotImplementedError("SQLite存储尚未实现")
    
    def save_character(self, character: Character) -> bool:
        """保存角色到数据库"""
        # TODO: 实现数据库保存
        raise NotImplementedError("SQLite存储尚未实现")
    
    def list_characters(self) -> List[str]:
        """列出所有角色"""
        # TODO: 实现数据库查询
        raise NotImplementedError("SQLite存储尚未实现")
    
    def delete_character(self, name: str) -> bool:
        """从数据库删除角色"""
        # TODO: 实现数据库删除
        raise NotImplementedError("SQLite存储尚未实现")