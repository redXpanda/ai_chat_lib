"""
角色数据模型
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class ExampleDialog:
    """示例对话"""
    user_message: str
    character_response: str
    
@dataclass 
class Character:
    """AI角色模型"""
    name: str
    description: str
    system_prompt: str
    example_dialogs: List[ExampleDialog]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description, 
            "system_prompt": self.system_prompt,
            "example_dialogs": [
                {"user_message": d.user_message, "character_response": d.character_response}
                for d in self.example_dialogs
            ],
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """从字典创建角色"""
        example_dialogs = [
            ExampleDialog(d["user_message"], d["character_response"])
            for d in data.get("example_dialogs", [])
        ]
        
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
            
        updated_at = None
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"])
        
        return cls(
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            example_dialogs=example_dialogs,
            metadata=data.get("metadata"),
            created_at=created_at,
            updated_at=updated_at
        )