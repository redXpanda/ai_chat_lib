"""
提示词管理器
"""
import re
from typing import Dict, Any, List, Optional
from .models.character import Character
from .models.message import MessageRole, Message

class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        self.global_variables = {}
    
    def set_variable(self, key: str, value: str):
        """设置全局变量"""
        self.global_variables[key] = value
    
    def render_prompt(self, template: str, character: Optional[Character] = None, 
                     user_name: str = "用户", **kwargs) -> str:
        """渲染提示词模板"""
        variables = {
            "user": user_name,
            "character": character.name if character else "AI助手",
            **self.global_variables,
            **kwargs
        }
        
        # 如果有角色信息，添加角色相关变量
        if character:
            variables.update({
                "character_name": character.name,
                "character_description": character.description
            })
        
        # 替换模板变量 {{variable}}
        def replace_var(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, template)
    
    def render_character_prompt(self, character: Character, user_name: str = "用户", 
                              **kwargs) -> str:
        """渲染角色的系统提示词"""
        return self.render_prompt(character.system_prompt, character, user_name, **kwargs)
    
    def render_chat_history(self, chat_history: List[Message], character: Optional[Character] = None, 
                     user_name: str = "用户", **kwargs) -> str:
        """渲染一个聊天记录列表"""
        for i, message in enumerate(chat_history):
            if message.role == MessageRole.USER:
                chat_history[i].content = self.render_prompt(message.content, character, user_name, **kwargs)
        