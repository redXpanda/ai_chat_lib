"""
AI角色管理器
"""
from typing import List, Optional
from .models.character import Character
from .storage.base import BaseStorage
from .storage.file_storage import FileStorage
from .models.message import Message, MessageRole


class CharacterManager:
    """AI角色管理器"""
    
    def __init__(self, storage: Optional[BaseStorage] = None):
        self.storage = storage or FileStorage()
        self._characters_cache = {}
    
    def load_character(self, name: str, use_cache: bool = True) -> Optional[Character]:
        """加载角色"""
        if use_cache and name in self._characters_cache:
            return self._characters_cache[name]
        
        character = self.storage.load_character(name)
        if character and use_cache:
            self._characters_cache[name] = character
        
        return character
    
    def character_example_chat_to_history(self, character: Character) -> List[Message]:
        """将角色的示例聊天记录转换为历史记录"""
        history = []
        for msg in character.example_dialogs:
            history.append(Message(role=MessageRole.USER, content=msg.user_message))
            history.append(Message(role=MessageRole.ASSISTANT, content=msg.character_response))

        return history
    
    def save_character(self, character: Character) -> bool:
        """保存角色"""
        success = self.storage.save_character(character)
        if success:
            self._characters_cache[character.name] = character
        return success
    
    def list_characters(self) -> List[str]:
        """列出所有可用角色"""
        return self.storage.list_characters()
    
    def delete_character(self, name: str) -> bool:
        """删除角色"""
        success = self.storage.delete_character(name)
        if success and name in self._characters_cache:
            del self._characters_cache[name]
        return success
    
    def update_character(self, character: Character) -> bool:
        """更新角色信息"""
        character.updated_at = datetime.now()
        return self.save_character(character)
    
    def clear_cache(self):
        """清空缓存"""
        self._characters_cache.clear()