"""
聊天数据适配器
"""
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from .models.message import Message, MessageRole
from .models.character import Character

class ModelAdapter(ABC):
    """模型适配器抽象基类"""
    
    @abstractmethod
    def format_messages(self, messages: List[Message], character: Character) -> List[Dict[str, Any]]:
        """格式化消息为特定模型格式"""
        pass
    
    def to_message(self, content: str) -> Message:
        """将Google AI返回的格式转换为Message对象"""
        return Message(role=MessageRole.ASSISTANT, content=content)
    
    
    @abstractmethod
    def supports_system_message(self) -> bool:
        """是否支持系统消息"""
        pass

class OpenAIAdapter(ModelAdapter):
    """OpenAI模型适配器"""
    
    def format_messages(self, messages: List[Message], character: Character) -> List[Dict[str, Any]]:
        """格式化为OpenAI格式"""
        formatted = []
        
        # 添加系统消息
        if self.supports_system_message():
            formatted.append({
                "role": "system",
                "content": character.system_prompt
            })
        
        # 添加示例对话
        for example in character.example_dialogs:
            formatted.append({
                "role": "user",
                "content": example.user_message
            })
            formatted.append({
                "role": "assistant", 
                "content": example.character_response
            })
        
        # 添加聊天历史
        for msg in messages:
            formatted.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return formatted
    
    def supports_system_message(self) -> bool:
        return True

class GoogleAIAdapter(ModelAdapter):
    """Google AI模型适配器"""
    
    def format_messages(self, messages: List[Message], character: Character) -> List[Dict[str, Any]]:
        """格式化为Google AI格式"""
        formatted = []
        
        # Google AI可能不支持系统消息，需要融合到用户消息中
        if not self.supports_system_message() and messages:
            # 将系统提示词融合到第一条用户消息中
            first_user_msg = None
            for i, msg in enumerate(messages):
                if msg.role == MessageRole.USER:
                    first_user_msg = i
                    break
            
            if first_user_msg is not None:
                enhanced_content = f"{character.system_prompt}\n\n{messages[first_user_msg].content}"
                messages[first_user_msg].content = enhanced_content
        
        # 转换消息格式
        for msg in messages:
            role_mapping = {
                MessageRole.USER.value: "user",
                MessageRole.ASSISTANT.value: "model",  # Google AI使用'model'而不是'assistant'
                MessageRole.SYSTEM.value: "user"  # 如果有系统消息，转换为用户消息
            }
            
            formatted.append({
                "role": role_mapping.get(msg.role.value, msg.role.value),
                "parts": [{"text": msg.content}]  # Google AI格式
            })
        
        return formatted
    

    def supports_system_message(self) -> bool:
        return True

class DataAdapter:
    """聊天数据适配器"""
    
    def __init__(self):
        self.adapters = {
            "openai": OpenAIAdapter(),
            "google": GoogleAIAdapter(),
        }
    
    def register_adapter(self, provider_name: str, adapter: ModelAdapter):
        """注册新的适配器"""
        self.adapters[provider_name] = adapter
    
    def format_for_provider(self, provider_name: str, messages: List[Message], 
                          character: Character) -> List[Dict[str, Any]]:
        """为指定提供商格式化消息"""
        if provider_name not in self.adapters:
            raise ValueError(f"不支持的提供商: {provider_name}")
        
        adapter = self.adapters[provider_name]
        return adapter.format_messages(messages, character)