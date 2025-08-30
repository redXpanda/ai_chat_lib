"""
角色创建工具
"""
from datetime import datetime
from ..models.character import Character, ExampleDialog

def create_sample_character() -> Character:
    """创建示例角色"""
    example_dialogs = [
        ExampleDialog(
            user_message="你好",
            character_response="你好！我是{{character}}，很高兴认识你！有什么我可以帮助你的吗？"
        ),
        ExampleDialog(
            user_message="你能做什么？",
            character_response="我可以和你聊天，回答问题，帮助你解决问题。让我们开始愉快的对话吧！"
        )
    ]
    
    return Character(
        name="友好助手",
        description="一个友善、乐于助人的AI助手角色",
        system_prompt="你是{{character}}，一个友善、乐于助人的AI助手。你总是用积极、友好的语气与{{user}}交流，并尽力帮助解决问题。",
        example_dialogs=example_dialogs,
        metadata={"category": "助手", "language": "zh-CN"},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
