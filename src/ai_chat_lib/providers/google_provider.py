"""
Google AI提供商实现
"""
from typing import List, Dict, Any, AsyncGenerator
import os
from google import genai
from google.genai import types
from .base import BaseAIProvider
from ai_chat_lib.models.message import Message


class GoogleAIProvider(BaseAIProvider):
    """Google AI提供商实现"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__(api_key, model)
        self.client = genai.Client(api_key=api_key)

    def get_provider_name(self) -> str:
        return "google"
    
    def get_supported_models(self) -> List[str]:
        return [
            "gemini-2.5-flash",
            "write_name_here",
        ]
    

    
    def _convert_messages_to_google_format(self, system: str, messages: List[Message]) -> List[types.Content]:
        """将标准消息格式转换为Google AI格式"""
        contents = []
        
        # 转换消息历史
        for message in messages:
            role = message.role
            content = message.content
            
            # Google AI API使用 "model" 而不是 "assistant"
            google_role = "model" if role == "assistant" else "user"
            
            contents.append(types.Content(
                role=google_role,  
                parts=[types.Part.from_text(text=content)]
            ))
        
        return contents
    
    async def chat_completion(self, system: str, messages: List[Dict[str, Any]], 
                            **kwargs) -> str:
        """Google AI聊天完成实现"""
        try:
            # 转换消息格式
            contents = self._convert_messages_to_google_format(system, messages)
            
            # 设置生成配置
            generate_content_config = types.GenerateContentConfig(
                max_output_tokens=kwargs.get("max_tokens", 1024),
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                media_resolution="MEDIA_RESOLUTION_LOW",
                # 可以根据需要添加工具
                # tools=[
                #     types.Tool(googleSearch=types.GoogleSearch())
                # ] if kwargs.get("enable_search", False) else None,

                system_instruction=[
                types.Part.from_text(text= system),
                ],
            )
            
            # 调用Google AI API
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            # 提取响应文本
            if response and response.text:
                return response.text
            else:
                return "抱歉，没有收到有效的响应。"
                
        except Exception as e:
            raise Exception(f"Google AI API调用失败: {str(e)}")
    
    async def chat_completion_stream(self, system: str, messages: List[Dict[str, Any]], 
                                   **kwargs) -> AsyncGenerator[str, None]:
        """Google AI流式聊天完成实现"""
        try:
            # 转换消息格式
            contents = self._convert_messages_to_google_format(system, messages)
            
            # 设置生成配置
            generate_content_config = types.GenerateContentConfig(
                max_output_tokens=kwargs.get("max_tokens", 1024),
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
                media_resolution="MEDIA_RESOLUTION_LOW",
                # 可以根据需要添加工具
                # tools=[
                #     types.Tool(googleSearch=types.GoogleSearch())
                # ] if kwargs.get("enable_search", False) else None,

                system_instruction=[
                types.Part.from_text(text= system),
                ]
            )
            
            # 流式调用Google AI API
            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise Exception(f"Google AI流式API调用失败: {str(e)}")
    
    def _validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            return False
        
        # 可以添加更多的验证逻辑
        return True


    
