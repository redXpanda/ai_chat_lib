
"""
OpenAI基础提供商实现
"""
from typing import List, Dict, Any, AsyncGenerator, Optional
import os
from openai import OpenAI, AsyncOpenAI

from ai_chat_lib.models.message import Message
from .base import BaseAIProvider


class OpenAIBaseProvider(BaseAIProvider):
    """OpenAI基础提供商实现，可作为其他兼容OpenAI API的平台的基类"""
    
    def __init__(self, api_key: str, model: str, base_url: str = None):
        super().__init__(api_key, model)
        self.base_url = base_url
        
        # 初始化同步和异步客户端
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)

    def get_provider_name(self) -> str:
        return "openai_base"
    
    def get_supported_models(self) -> List[str]:
        """子类应该重写此方法以返回支持的模型列表"""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ]
    
    def _convert_messages_to_openai_format(self, system: str, messages: List[Message]) -> List[Dict[str, Any]]:
        """将标准消息格式转换为OpenAI格式"""
        openai_messages = []
        
        # 添加系统消息
        if system:
            openai_messages.append({
                "role": "system",
                "content": system
            })
        
        # 转换消息历史
        for message in messages:
            openai_messages.append({
                "role": message.role.value,
                "content": message.content
            })
        
        return openai_messages
    
    def _get_completion_kwargs(self, **kwargs) -> Dict[str, Any]:
        """构建API调用的参数，子类可以重写以添加特定参数"""
        completion_kwargs = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
        }
        
        # 添加额外的body参数（用于一些特殊功能，如思考模式）
        extra_body = kwargs.get("extra_body", {})
        if extra_body:
            completion_kwargs["extra_body"] = extra_body
            
        return completion_kwargs
    
    async def chat_completion(self, system: str, messages: List[Dict[str, Any]], 
                            **kwargs) -> str:
        """OpenAI聊天完成实现"""
        try:
            # 转换消息格式
            openai_messages = self._convert_messages_to_openai_format(system, messages)
            
            # 获取完成参数
            completion_kwargs = self._get_completion_kwargs(**kwargs)
            completion_kwargs["messages"] = openai_messages
            
            # 调用OpenAI API
            response = await self.async_client.chat.completions.create(**completion_kwargs)
            
            # 提取响应文本
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                return "抱歉，没有收到有效的响应。"
                
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    async def chat_completion_stream(self, system: str, messages: List[Dict[str, Any]], 
                                   **kwargs) -> AsyncGenerator[str, None]:
        """OpenAI流式聊天完成实现"""
        try:
            # 转换消息格式
            openai_messages = self._convert_messages_to_openai_format(system, messages)
            
            # 获取完成参数
            completion_kwargs = self._get_completion_kwargs(**kwargs)
            completion_kwargs["messages"] = openai_messages
            completion_kwargs["stream"] = True
            
            # 可选：添加流式选项
            stream_options = kwargs.get("stream_options")
            if stream_options:
                completion_kwargs["stream_options"] = stream_options
            
            # 流式调用OpenAI API
            stream = await self.async_client.chat.completions.create(**completion_kwargs)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI流式API调用失败: {str(e)}")
    
    async def chat_completion_stream_with_reasoning(self, system: str, messages: List[Dict[str, Any]], 
                                                  **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """支持思考过程的流式聊天完成（适用于支持reasoning的模型）"""
        try:
            # 转换消息格式
            openai_messages = self._convert_messages_to_openai_format(system, messages)
            
            # 获取完成参数并启用思考模式
            completion_kwargs = self._get_completion_kwargs(**kwargs)
            completion_kwargs["messages"] = openai_messages
            completion_kwargs["stream"] = True
            
            # 确保启用思考模式
            if "extra_body" not in completion_kwargs:
                completion_kwargs["extra_body"] = {}
            completion_kwargs["extra_body"]["enable_thinking"] = True
            
            # 流式调用API
            stream = await self.async_client.chat.completions.create(**completion_kwargs)
            
            reasoning_content = ""
            answer_content = ""
            is_answering = False
            
            async for chunk in stream:
                if not chunk.choices:
                    # 处理使用情况信息
                    if hasattr(chunk, 'usage') and chunk.usage:
                        yield {
                            "type": "usage",
                            "data": chunk.usage
                        }
                    continue
                
                delta = chunk.choices[0].delta
                
                # 处理思考内容
                if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                    reasoning_content += delta.reasoning_content
                    if not is_answering:
                        yield {
                            "type": "reasoning",
                            "data": delta.reasoning_content
                        }
                
                # 处理回复内容
                if hasattr(delta, "content") and delta.content:
                    if not is_answering:
                        is_answering = True
                        yield {
                            "type": "answer_start",
                            "data": None
                        }
                    
                    answer_content += delta.content
                    yield {
                        "type": "answer",
                        "data": delta.content
                    }
            
            # 发送完整内容
            yield {
                "type": "complete",
                "data": {
                    "reasoning": reasoning_content,
                    "answer": answer_content
                }
            }
                    
        except Exception as e:
            raise Exception(f"OpenAI思考模式流式API调用失败: {str(e)}")
    
    def _validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            return False
        
        try:
            # 简单的连接测试
            models = self.client.models.list()
            return True
        except Exception:
            return False
    
    def get_client_config(self) -> Dict[str, Any]:
        """获取客户端配置信息"""
        return {
            "api_key": self.api_key[:10] + "..." if self.api_key else None,
            "model": self.model,
            "base_url": self.base_url,
            "provider": self.get_provider_name()
        }


class OpenAIProvider(OpenAIBaseProvider):
    """标准OpenAI提供商实现"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key, model, base_url=None)

    def get_provider_name(self) -> str:
        return "openai"

