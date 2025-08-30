"""
存储基类
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.character import Character

class BaseStorage(ABC):
    """存储抽象基类"""
    
    @abstractmethod
    def load_character(self, name: str) -> Optional[Character]:
        """加载角色"""
        pass
    
    @abstractmethod
    def save_character(self, character: Character) -> bool:
        """保存角色"""
        pass
    
    @abstractmethod
    def list_characters(self) -> List[str]:
        """列出所有角色名称"""
        pass
    
    @abstractmethod
    def delete_character(self, name: str) -> bool:
        """删除角色"""
        pass
