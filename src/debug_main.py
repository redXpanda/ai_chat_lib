# 使用示例和测试代码
import os


if __name__ == "__main__":
    import asyncio
    
    # 创建示例角色文件
    def create_example_characters():
        """创建示例角色文件"""
        import os
        
        from ai_chat_lib.storage.file_storage import DEFAULT_CHARACTERS_DIR
        characters_dir = DEFAULT_CHARACTERS_DIR
        os.makedirs(characters_dir, exist_ok=True)
        
        # 创建友好助手角色文件
        assistant_content = '''"""
友好助手角色配置文件
"""

CHARACTER_DATA = {
    "name": "友好助手",
    "description": "一个友善、乐于助人的AI助手角色",
    "system_prompt": """你是{{character}}，一个友善、乐于助人的AI助手。你总是用积极、友好的语气与{{user}}交流，并尽力帮助解决问题。请记住：
- 保持友善和耐心
- 提供有用的建议
- 如果不确定答案，要诚实说明""",
    "example_dialogs": [
        {
            "user_message": "你好",
            "character_response": "你好！我是{{character}}，很高兴认识你！有什么我可以帮助你的吗？"
        },
        {
            "user_message": "你能做什么？", 
            "character_response": "我可以和你聊天，回答问题，帮助你解决问题。让我们开始愉快的对话吧！"
        }
    ],
    "metadata": {"category": "助手", "language": "zh-CN"}
}
'''
        
        # 创建编程专家角色文件
        programmer_content = '''"""
编程专家角色配置文件
"""

CHARACTER_DATA = {
    "name": "编程专家",
    "description": "专业的编程助手，擅长多种编程语言和技术栈",
    "system_prompt": """你是{{character}}，一位经验丰富的编程专家。你具备以下特点：
- 精通多种编程语言（Python、JavaScript、Java、C++等）
- 熟悉各种开发框架和工具
- 能够提供清晰的代码示例和解释
- 注重代码质量和最佳实践
- 耐心解答{{user}}的编程问题""",
    "example_dialogs": [
        {
            "user_message": "如何用Python创建一个简单的类？",
            "character_response": "很好的问题！在Python中创建类很简单。这里是一个基本示例：\\n\\n```python\\nclass Person:\\n    def __init__(self, name, age):\\n        self.name = name\\n        self.age = age\\n    \\n    def introduce(self):\\n        return f'我是{self.name}，今年{self.age}岁'\\n```\\n\\n这个类有构造函数和一个方法。你想了解更多细节吗？"
        }
    ],
    "metadata": {"category": "专业", "language": "zh-CN", "expertise": "programming"}
}
'''
        
        # 写入文件
        with open(os.path.join(characters_dir, "友好助手.py"), 'w', encoding='utf-8') as f:
            f.write(assistant_content)
            
        with open(os.path.join(characters_dir, "编程专家.py"), 'w', encoding='utf-8') as f:
            f.write(programmer_content)
        
        print("示例角色文件已创建！")
    
    
    async def demo():
        """演示用法"""
        print("=== AI Chat Library 演示 ===\n")
        
        # 创建示例角色文件
        create_example_characters()

        from ai_chat_lib.chat_interface import ChatInterface
        from ai_chat_lib.providers.google_provider import GoogleAIProvider
        from ai_chat_lib.models.message import MessageRole
        
        # 初始化组件
        chat = ChatInterface()
        
        # 列出可用角色
        available_characters = chat.character_manager.list_characters()
        print("可用角色:", available_characters)
        
        # 切换到友好助手角色
        if "友好助手" in available_characters:
            success = chat.switch_character("友好助手")
            print(f"切换角色: {'成功' if success else '失败'}")
            
            if success:
                character = chat.get_current_character()
                print(f"当前角色: {character.name}")
                print(f"角色描述: {character.description}\n")
        
        # 设置模拟提供商
        mock_provider = GoogleAIProvider(os.environ["GEMINI_API_KEY"], "gemini-2.5-flash")
        chat.switch_provider(mock_provider)
        print(f"当前提供商: {chat.get_current_provider().get_provider_name()}")
        print(f"当前模型: {chat.get_current_provider().model}\n")
        
        # 设置提示词变量
        chat.prompt_manager.set_variable("user", "潘达")
        
        # 模拟聊天
        print("=== 开始聊天 ===")
        test_messages = [
            "你好，{{character}}！",
            "你能介绍一下自己吗？",
            "谢谢你的帮助！"
        ]
        
        for user_msg in test_messages:
            print(f"用户: {user_msg}")
            try:
                response = await chat.chat(user_msg)
                print(f"AI: {response}\n")
            except Exception as e:
                print(f"聊天出错: {e}\n")
        
        # 显示聊天历史
        print("=== 聊天历史 ===")
        history = chat.get_chat_history()
        for i, msg in enumerate(history):
            role_name = "用户" if msg.role == MessageRole.USER else "AI"
            print(f"{i+1}. {role_name}: {msg.content}...")
        
        print(f"\n总计消息数: {len(history)}")
        
        # 显示历史摘要
        summary = chat.get_history_summary()
        print("\n=== 会话摘要 ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
    
# 运行演示
asyncio.run(demo())