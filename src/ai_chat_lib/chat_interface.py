"""
最终聊天接口
"""
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from .models.message import Message, MessageRole
from .models.character import Character
from .character_manager import CharacterManager
from .data_adapter import DataAdapter
from .prompt_manager import PromptManager
from .providers.base import BaseAIProvider

class ChatInterface:
    """聊天接口"""
    
    def __init__(self, character_manager: Optional[CharacterManager] = None,
                 data_adapter: Optional[DataAdapter] = None,
                 prompt_manager: Optional[PromptManager] = None):
        self.character_manager = character_manager or CharacterManager()
        self.data_adapter = data_adapter or DataAdapter()
        self.prompt_manager = prompt_manager or PromptManager()
        
        # 聊天状态
        self.current_character: Optional[Character] = None
        self.current_provider: Optional[BaseAIProvider] = None
        self.chat_history: List[Message] = []
        self.last_user_message: Optional[Message] = None
        self.session_id: str = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def switch_character(self, character_name: str) -> bool:
        """切换AI角色"""
        character = self.character_manager.load_character(character_name)
        if character:
            self.current_character = character
            # 切换角色时清空历史记录
            self.clear_history()
            # 把角色示例对话插入到历史中
            example_history = self.character_manager.character_example_chat_to_history(self.current_character)
            self.chat_history.extend(example_history)
            self.prompt_manager.render_chat_history(self.chat_history, self.current_character
                                                    , user_name=self.prompt_manager.global_variables.get("user", "user")
            )
            return True
        return False
    
    def switch_provider(self, provider: BaseAIProvider) -> bool:
        """切换AI提供商"""
        try:
            self.current_provider = provider
            return True
        except Exception as e:
            print(f"切换提供商失败: {e}")
            return False
    
    def get_current_character(self) -> Optional[Character]:
        """获取当前角色"""
        return self.current_character
    
    def get_current_provider(self) -> Optional[BaseAIProvider]:
        """获取当前提供商"""
        return self.current_provider
    
    def prepare_chat(self, user_input: str, user_name: str = "用户", **kwargs):
        """发送聊天消息并获取回复"""
        if not self.current_character:
            raise ValueError("请先设置AI角色")
        
        if not self.current_provider:
            raise ValueError("请先设置AI提供商")
        
        # 渲染用户输入中的模板变量
        rendered_input = self.prompt_manager.render_prompt(
            user_input, self.current_character, user_name, **kwargs
        )

        system_input = self.prompt_manager.render_character_prompt(
            self.current_character, user_name, **kwargs
        )
        
        # 添加用户消息到历史
        user_message = Message(
            role=MessageRole.USER,
            content=rendered_input,
            timestamp=datetime.now()
        )
        self.chat_history.append(user_message)
        self.last_user_message = user_message

        self.chat_history = self.current_provider.resolve_chat_history_with_system(system_input, self.chat_history)

        return system_input, self.chat_history



    async def chat(self, user_input: str, user_name: str = "用户", **kwargs) -> str:
        system_input, self.chat_history = self.prepare_chat(user_input, user_name, **kwargs)
        
        # 调用AI提供商获取回复
        try:
            response = await self.current_provider.chat_completion(
                system_input, self.chat_history, **kwargs
            )
            
            # 添加AI回复到历史
            ai_message = Message(
                role=MessageRole.ASSISTANT,
                content=response,
                timestamp=datetime.now()
            )
            self.chat_history.append(ai_message)
            
            return response
        
        except Exception as e:
            # 如果发生错误，移除刚添加的用户消息
            if self.chat_history and self.last_user_message and self.chat_history[-1] == self.last_user_message:
                self.chat_history.pop()
            raise e
    
    async def chat_stream(self, user_input: str, user_name: str = "用户", 
                         **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        system_input, self.chat_history = self.prepare_chat(user_input, user_name, **kwargs)
        
        # 流式获取回复
        full_response = ""
        try:
            async for chunk in self.current_provider.chat_completion_stream(
                system_input, self.chat_history, **kwargs
            ):
                full_response += chunk
                yield chunk
            
            # 添加完整回复到历史
            ai_message = Message(
                role=MessageRole.ASSISTANT,
                content=full_response,
                timestamp=datetime.now()
            )
            self.chat_history.append(ai_message)
            
        except Exception as e:
            # 如果发生错误，移除刚添加的用户消息
            if self.chat_history and self.last_user_message and self.chat_history[-1] == self.last_user_message:
                self.chat_history.pop()
            raise e
    
    def get_chat_history(self) -> List[Message]:
        """获取聊天历史"""
        return self.chat_history.copy()
    
    def clear_history(self):
        """清空聊天历史"""
        self.chat_history.clear()
    
    def get_history_summary(self) -> Dict[str, Any]:
        """获取历史摘要信息"""
        return {
            "session_id": self.session_id,
            "character": self.current_character.name if self.current_character else None,
            "provider": self.current_provider.get_provider_name() if self.current_provider else None,
            "message_count": len(self.chat_history),
            "created_at": datetime.now().isoformat()
        }