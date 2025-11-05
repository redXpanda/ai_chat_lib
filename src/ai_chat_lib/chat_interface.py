"""
多会话聊天接口
"""
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass
from .models.message import Message, MessageRole
from .models.character import Character
from .character_manager import CharacterManager
from .data_adapter import DataAdapter
from .prompt_manager import PromptManager
from .providers.base import BaseAIProvider

@dataclass
class ChatSession:
    """聊天会话"""
    session_id: str
    character: Optional[Character] = None
    provider: Optional[BaseAIProvider] = None
    chat_history: List[Message] = None
    last_user_message: Optional[Message] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.chat_history is None:
            self.chat_history = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class MultiSessionChatInterface:
    """多会话聊天接口"""
    
    def __init__(self, character_manager: Optional[CharacterManager] = None,
                 data_adapter: Optional[DataAdapter] = None,
                 prompt_manager: Optional[PromptManager] = None):
        self.character_manager = character_manager or CharacterManager()
        self.data_adapter = data_adapter or DataAdapter()
        self.prompt_manager = prompt_manager or PromptManager()
        
        # 会话管理
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """创建新会话"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        if session_id in self.sessions:
            #raise ValueError(f"会话 {session_id} 已存在")
            return ""
        
        session = ChatSession(session_id=session_id)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        
        return session_id
    
    def switch_session(self, session_id: str) -> bool:
        """切换当前会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            return True
        self.create_session(session_id)
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            if self.current_session_id == session_id:
                self.current_session_id = None
            del self.sessions[session_id]
            return True
        return False
    
    def get_current_session(self) -> Optional[ChatSession]:
        """获取当前会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取指定会话"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        return [
            {
                "session_id": session.session_id,
                "character": session.character.name if session.character else None,
                "provider": session.provider.get_provider_name() if session.provider else None,
                "message_count": len(session.chat_history),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "is_current": session.session_id == self.current_session_id
            }
            for session in self.sessions.values()
        ]
    
    def switch_character(self, character_name: str, session_id: Optional[str] = None) -> bool:
        """为指定会话切换AI角色"""
        if session_id is None:
            session_id = self.current_session_id
        
        if session_id is None:
            raise ValueError("没有当前会话，请先创建或切换会话")
        
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")
        
        character = self.character_manager.load_character(character_name)
        if character:
            session.character = character
            # 切换角色时清空历史记录
            session.chat_history.clear()
            # 把角色示例对话插入到历史中
            example_history = self.character_manager.character_example_chat_to_history(character)
            session.chat_history.extend(example_history)
            session.updated_at = datetime.now()
            return True
        return False
    
    def switch_provider(self, provider: BaseAIProvider, session_id: Optional[str] = None) -> bool:
        """为指定会话切换AI提供商"""
        if session_id is None:
            session_id = self.current_session_id
        
        if session_id is None:
            raise ValueError("没有当前会话，请先创建或切换会话")
        
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")
        
        try:
            session.provider = provider
            session.updated_at = datetime.now()
            return True
        except Exception as e:
            print(f"切换提供商失败: {e}")
            return False
    
    def get_character(self, session_id: Optional[str] = None) -> Optional[Character]:
        """获取指定会话的当前角色"""
        if session_id is None:
            session_id = self.current_session_id
        
        session = self.sessions.get(session_id) if session_id else None
        return session.character if session else None
    
    def get_provider(self, session_id: Optional[str] = None) -> Optional[BaseAIProvider]:
        """获取指定会话的当前提供商"""
        if session_id is None:
            session_id = self.current_session_id
        
        session = self.sessions.get(session_id) if session_id else None
        return session.provider if session else None
    
    def prepare_chat(self, user_input: str, user_name: str = "用户", 
                    session_id: Optional[str] = None, **kwargs):
        """准备聊天消息"""
        if session_id is None:
            session_id = self.current_session_id
        
        if session_id is None:
            raise ValueError("没有当前会话，请先创建或切换会话")
        
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")
        
        if not session.character:
            raise ValueError(f"会话 {session_id} 未设置AI角色")
        
        if not session.provider:
            raise ValueError(f"会话 {session_id} 未设置AI提供商")
        
        # 渲染用户输入中的模板变量
        rendered_input = self.prompt_manager.render_prompt(
            user_input, session.character, user_name, **kwargs
        )

        system_input = self.prompt_manager.render_character_prompt(
            session.character, user_name, **kwargs
        )
        
        # 添加用户消息到历史
        user_message = Message(
            role=MessageRole.USER,
            content=rendered_input,
            timestamp=datetime.now()
        )
        session.chat_history.append(user_message)
        session.last_user_message = user_message
        session.updated_at = datetime.now()

        session.chat_history = session.provider.resolve_chat_history_with_system(
            system_input, session.chat_history
        )

        return system_input, session.chat_history, session

    async def chat(self, user_input: str, user_name: str = "用户", 
                  session_id: Optional[str] = None, **kwargs) -> str:
        """发送聊天消息并获取回复"""
        system_input, chat_history, session = self.prepare_chat(
            user_input, user_name, session_id, **kwargs
        )
        
        # 调用AI提供商获取回复
        try:
            response = await session.provider.chat_completion(
                system_input, chat_history, **kwargs
            )
            
            # 添加AI回复到历史
            ai_message = Message(
                role=MessageRole.ASSISTANT,
                content=response,
                timestamp=datetime.now()
            )
            session.chat_history.append(ai_message)
            session.updated_at = datetime.now()
            
            return response
        
        except Exception as e:
            # 如果发生错误，移除刚添加的用户消息
            if (session.chat_history and session.last_user_message and 
                session.chat_history[-1] == session.last_user_message):
                session.chat_history.pop()
            raise e
    
    async def chat_stream(self, user_input: str, user_name: str = "用户", 
                         session_id: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        system_input, chat_history, session = self.prepare_chat(
            user_input, user_name, session_id, **kwargs
        )
        
        # 流式获取回复
        full_response = ""
        try:
            async for chunk in session.provider.chat_completion_stream(
                system_input, chat_history, **kwargs
            ):
                full_response += chunk
                yield chunk
            
            # 添加完整回复到历史
            ai_message = Message(
                role=MessageRole.ASSISTANT,
                content=full_response,
                timestamp=datetime.now()
            )
            session.chat_history.append(ai_message)
            session.updated_at = datetime.now()
            
        except Exception as e:
            # 如果发生错误，移除刚添加的用户消息
            if (session.chat_history and session.last_user_message and 
                session.chat_history[-1] == session.last_user_message):
                session.chat_history.pop()
            raise e
    
    def get_chat_history(self, session_id: Optional[str] = None) -> List[Message]:
        """获取指定会话的聊天历史"""
        if session_id is None:
            session_id = self.current_session_id
        
        session = self.sessions.get(session_id) if session_id else None
        return session.chat_history.copy() if session else []
    
    def clear_history(self, session_id: Optional[str] = None):
        """清空指定会话的聊天历史"""
        if session_id is None:
            session_id = self.current_session_id
        
        session = self.sessions.get(session_id) if session_id else None
        if session:
            session.chat_history.clear()
            session.updated_at = datetime.now()
    
    def get_session_summary(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取指定会话的摘要信息"""
        if session_id is None:
            session_id = self.current_session_id
        
        session = self.sessions.get(session_id) if session_id else None
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "character": session.character.name if session.character else None,
            "provider": session.provider.get_provider_name() if session.provider else None,
            "message_count": len(session.chat_history),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "is_current": session.session_id == self.current_session_id
        }

# 保持向后兼容的单会话接口
class ChatInterface:
    """单会话聊天接口（向后兼容）"""
    
    def __init__(self, character_manager: Optional[CharacterManager] = None,
                 data_adapter: Optional[DataAdapter] = None,
                 prompt_manager: Optional[PromptManager] = None):
        self.multi_chat = MultiSessionChatInterface(character_manager, data_adapter, prompt_manager)
        # 自动创建一个默认会话
        self.session_id = self.multi_chat.create_session()
        self.character_manager = self.multi_chat.character_manager
        self.prompt_manager = self.multi_chat.prompt_manager
    
    def switch_character(self, character_name: str) -> bool:
        """切换AI角色"""
        return self.multi_chat.switch_character(character_name, self.session_id)
    
    def switch_provider(self, provider: BaseAIProvider) -> bool:
        """切换AI提供商"""
        return self.multi_chat.switch_provider(provider, self.session_id)
    
    def get_current_character(self) -> Optional[Character]:
        """获取当前角色"""
        return self.multi_chat.get_character(self.session_id)
    
    def get_current_provider(self) -> Optional[BaseAIProvider]:
        """获取当前提供商"""
        return self.multi_chat.get_provider(self.session_id)
    
    def prepare_chat(self, user_input: str, user_name: str = "用户", **kwargs):
        """发送聊天消息并获取回复"""
        system_input, chat_history, session = self.multi_chat.prepare_chat(
            user_input, user_name, self.session_id, **kwargs
        )
        return system_input, chat_history

    async def chat(self, user_input: str, user_name: str = "用户", **kwargs) -> str:
        return await self.multi_chat.chat(user_input, user_name, self.session_id, **kwargs)
    
    async def chat_stream(self, user_input: str, user_name: str = "用户", 
                         **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天"""
        async for chunk in self.multi_chat.chat_stream(user_input, user_name, self.session_id, **kwargs):
            yield chunk
    
    def get_chat_history(self) -> List[Message]:
        """获取聊天历史"""
        return self.multi_chat.get_chat_history(self.session_id)
    
    def clear_history(self):
        """清空聊天历史"""
        self.multi_chat.clear_history(self.session_id)
    
    def get_history_summary(self) -> Dict[str, Any]:
        """获取历史摘要信息"""
        return self.multi_chat.get_session_summary(self.session_id)

# 使用示例
"""
# 创建多会话接口
multi_chat = MultiSessionChatInterface()

# 创建会话
session1 = multi_chat.create_session("chat_with_alice")
session2 = multi_chat.create_session("chat_with_bob")

# 为不同会话设置不同的角色和提供商
multi_chat.switch_character("助手", "chat_with_alice")
multi_chat.switch_provider(openai_provider, "chat_with_alice")

multi_chat.switch_character("翻译", "chat_with_bob")
multi_chat.switch_provider(claude_provider, "chat_with_bob")

# 在不同会话中聊天
response1 = await multi_chat.chat("你好", session_id="chat_with_alice")
response2 = await multi_chat.chat("Hello", session_id="chat_with_bob")

# 列出所有会话
sessions = multi_chat.list_sessions()

# 切换当前会话
multi_chat.switch_session("chat_with_alice")

# 使用当前会话聊天（不需要指定session_id）
response = await multi_chat.chat("今天天气怎么样？")
"""