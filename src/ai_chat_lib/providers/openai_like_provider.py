
from typing import List
from ai_chat_lib.providers.openai_base_provider import OpenAIBaseProvider


class DeepSeekProvider(OpenAIBaseProvider):
    """DeepSeek提供商实现（基于OpenAI兼容API）"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(
            api_key, 
            model, 
            base_url="https://api.deepseek.com"
        )

    def get_provider_name(self) -> str:
        return "deepseek"
    
    def get_supported_models(self) -> List[str]:
        return [
            "deepseek-chat",
        ]


class AliYunProvider(OpenAIBaseProvider):
    """阿里云百炼提供商实现（基于OpenAI兼容API）"""
    
    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        super().__init__(
            api_key, 
            model, 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def get_provider_name(self) -> str:
        return "aliyun"
    
    def get_supported_models(self) -> List[str]:
        return [
            "qwen-turbo",
            "qwen-plus", 
            "qwen-max",
            "qwen2.5-72b-instruct",
        ]