# 使用示例和测试代码
import os

from ai_chat_lib.providers.openai_like_provider import DeepSeekProvider


if __name__ == "__main__":
    import asyncio
    
    async def demo():
        """演示用法"""
        print("\n=== AI Chat Library 演示 ===\n")

        # 加载 .env 文件
        from dotenv import load_dotenv
        load_dotenv()
      

        from ai_chat_lib.chat_interface import ChatInterface
        from ai_chat_lib.providers.google_provider import GoogleAIProvider
        from ai_chat_lib.models.message import MessageRole
        
        # 初始化组件
        chat = ChatInterface()
        
        # 列出可用角色
        available_characters = chat.character_manager.list_characters()
        print("可用角色:", available_characters)

        # 设置提示词变量
        chat.prompt_manager.set_variable("user", "Brign")
        
        # 切换角色
        to_character = "myassis"
        if to_character in available_characters:
            success = chat.switch_character(to_character)
            print(f"切换角色: {'成功' if success else '失败'}")
            
            if success:
                character = chat.get_current_character()
                print(f"character: {character.name}")
                print(f"desc: {character.description}\n")
        
        # set provider
        google_provider = GoogleAIProvider(os.getenv("GEMINI_API_KEY"))
        deepseek_provider = DeepSeekProvider(os.getenv("DEEP_SEEK_API_KEY"))

        chat.switch_provider(google_provider)
        print(f"api provider: {chat.get_current_provider().get_provider_name()}")
        print(f"model: {chat.get_current_provider().model}\n")
        
        print("=== start ===")


        while True:
            command = input("You:")
            if command == "close":
                break
            else:
                ##print(f"You：{command}")
                try:

                    # 调用
                    ##res = await chat.chat(command)
                    ##print("{to_character}: {res}")

                    # 流式调用
                    print(f"\n{to_character}:")
                    res = ""
                    async for chunk in chat.chat_stream(command):
                        print(chunk, end="", flush=True)
                        res += chunk
                    print()

                    # write to md file
                    with open("chat.md", "a", encoding="utf-8") as f:
                        f.write(f"# You：\n ## {command}\n\n")
                        f.write(f"# Bot：\n ## {res}\n\n")
                except Exception as e:
                    print(f"error：{e}")
        
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