
# AI Chat Library
一个灵活、可扩展的AI聊天库，支持多种AI提供商和角色管理。

## 背景
ai生成的代码，ai生成的readme，用于ai的ai库，纯纯的ai.

我不太懂python，纯ai教的。

后面有空再细化吧，目前来看，能用就行。

用法请参考debug_*.py文件。

为什么放这？因为放这里直接f5调试方便，如果有别的更优雅的调试方式请告诉我。

## 特性

- 🎭 **角色管理**: 运行时加载和更新AI角色信息
- 🔌 **多提供商支持**: 支持OpenAI、Google AI等多个AI提供商
- 🔄 **数据适配**: 自动适配不同AI模型的消息格式
- 📝 **提示词管理**: 支持模板变量替换和动态提示词生成
- 💾 **灵活存储**: 支持文件存储和SQLite数据库存储
- 🚀 **异步支持**: 支持异步聊天和流式响应

## 快速开始

### 安装

```bash
poetry install
```

### 基本使用

```python
import asyncio
from ai_chat import ChatInterface, CharacterManager
from ai_chat.providers.openai_provider import OpenAIProvider

async def main():
    # 初始化聊天接口
    chat = ChatInterface()
    
    # 设置AI提供商
    provider = OpenAIProvider(api_key="your-api-key", model="gpt-3.5-turbo")
    chat.switch_provider(provider)
    
    # 切换角色
    chat.switch_character("友好助手")
    
    # 开始聊天
    response = await chat.chat("你好！")
    print(response)

asyncio.run(main())
```

### 创建自定义角色

在`characters/`目录下创建Python文件：

```python
# characters/my_character.py
CHARACTER_DATA = {
    "name": "我的角色",
    "description": "角色描述",
    "system_prompt": "你是{{character}}，一个专业的助手...",
    "example_dialogs": [
        {
            "user_message": "示例问题",
            "character_response": "示例回答"
        }
    ],
    "metadata": {"category": "自定义"}
}
```

## API文档

### CharacterManager

角色管理器，负责加载、保存和管理AI角色。

### DataAdapter

数据适配器，将通用消息格式转换为特定AI提供商的格式。

### PromptManager

提示词管理器，处理模板变量替换和提示词渲染。

### ChatInterface

主要聊天接口，整合所有组件提供统一的聊天功能。

## 扩展性

### 添加新的AI提供商

继承`BaseAIProvider`类并实现相应方法：

```python
from ai_chat.providers.base import BaseAIProvider

class MyAIProvider(BaseAIProvider):
    async def chat_completion(self, messages, **kwargs):
        # 实现你的API调用
        pass
    
    def get_provider_name(self):
        return "my_provider"
```

### 自定义存储后端

继承`BaseStorage`类实现自定义存储：

```python
from ai_chat.storage.base import BaseStorage

class MyStorage(BaseStorage):
    def load_character(self, name):
        # 实现你的存储逻辑
        pass
```