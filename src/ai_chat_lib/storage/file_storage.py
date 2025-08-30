"""
文件存储实现
"""
import os
import importlib.util
from typing import List, Optional, Dict, Any
from datetime import datetime
from .base import BaseStorage
from ..models.character import Character, ExampleDialog

DEFAULT_CHARACTERS_DIR = "storage/characters"

class FileStorage(BaseStorage):
    """基于Python文件的存储实现"""
    
    def __init__(self, characters_dir: str = DEFAULT_CHARACTERS_DIR):
        self.characters_dir = characters_dir
        os.makedirs(characters_dir, exist_ok=True)
    
    def load_character(self, name: str) -> Optional[Character]:
        """从Python文件加载角色"""
        file_path = os.path.join(self.characters_dir, f"{name}.py")
        if not os.path.exists(file_path):
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取角色数据
            character_data = getattr(module, 'CHARACTER_DATA', {})
            
            # 转换示例对话
            example_dialogs = []
            for dialog in character_data.get('example_dialogs', []):
                example_dialogs.append(ExampleDialog(
                    user_message=dialog['user_message'],
                    character_response=dialog['character_response']
                ))
            
            return Character(
                name=character_data.get('name', name),
                description=character_data.get('description', ''),
                system_prompt=character_data.get('system_prompt', ''),
                example_dialogs=example_dialogs,
                metadata=character_data.get('metadata', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"加载角色 {name} 失败: {e}")
            return None
    
    def save_character(self, character: Character) -> bool:
        """保存角色到Python文件"""
        file_path = os.path.join(self.characters_dir, f"{character.name}.py")
        
        try:
            # 生成Python文件内容
            content = self._generate_character_file(character)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"保存角色 {character.name} 失败: {e}")
            return False
    
    def list_characters(self) -> List[str]:
        """列出所有角色"""
        characters = []
        for file in os.listdir(self.characters_dir):
            if file.endswith('.py') and not file.startswith('__'):
                characters.append(file[:-3])  # 去掉.py后缀
        return characters
    
    def delete_character(self, name: str) -> bool:
        """删除角色文件"""
        file_path = os.path.join(self.characters_dir, f"{name}.py")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除角色 {name} 失败: {e}")
            return False
    
    def _generate_character_file(self, character: Character) -> str:
        """生成角色文件内容"""
        example_dialogs_str = "[\n"
        for dialog in character.example_dialogs:
            example_dialogs_str += f'    {{\n'
            example_dialogs_str += f'        "user_message": """{dialog.user_message}""",\n'
            example_dialogs_str += f'        "character_response": """{dialog.character_response}"""\n'
            example_dialogs_str += f'    }},\n'
        example_dialogs_str += "]"
        
        return f'''"""
{character.name} 角色配置文件
"""

CHARACTER_DATA = {{
    "name": "{character.name}",
    "description": """{character.description}""",
    "system_prompt": """{character.system_prompt}""",
    "example_dialogs": {example_dialogs_str},
    "metadata": {character.metadata or {}}
}}
'''
