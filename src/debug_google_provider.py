
from ai_chat_lib.providers.google_provider import GoogleAIProvider
import os
import pytest

# 使用示例
@pytest.mark.asyncio
async def test_example_usage():
    """使用示例"""
    # 初始化提供商
    provider = GoogleAIProvider(
        api_key=os.environ.get("GEMINI_API_KEY"),
        model="gemini-2.5-flash"
    )
    
    # 示例消息
    system_message = "你是一个有用的AI助手，请用中文回答问题。"
    messages = [
        {"role": "user", "content": "你好，请介绍一下自己。"},
        {"role": "assistant", "content": "你好！我是Google的AI助手，很高兴为您服务。"},
        {"role": "user", "content": "计算 90^3 等于多少？"}
    ]
    
    try:
        # 普通调用
        response = await provider.chat_completion(system_message, messages)
        print("响应:", response)
        
        # 流式调用
        print("\n流式响应:")
        async for chunk in provider.chat_completion_stream(system_message, messages):
            print(chunk, end="", flush=True)
        print()
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_example_usage())
