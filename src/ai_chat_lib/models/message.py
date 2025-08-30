"""
消息数据模型
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

class MessageRole(Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"

@dataclass
class Message:
    """聊天消息"""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建消息"""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
            
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=timestamp,
            metadata=data.get("metadata")
        )