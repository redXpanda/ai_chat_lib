"""
AI提供商抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator

class BaseAIProvider(ABC):
    """AI提供商抽象基类"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def resolve_chat_history_with_system(self, system, history) -> str:
        """处理系统提示词和聊天历史，某些model需要整合system到聊天历史中"""
        return history
    
    @abstractmethod
    async def chat_completion(self, system:str, messages: List[Dict[str, Any]], 
                            **kwargs) -> str:
        """聊天完成"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, system:str, messages: List[Dict[str, Any]], 
                                   **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """获取支持的模型列表"""
        pass