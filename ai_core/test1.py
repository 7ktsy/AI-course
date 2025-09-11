from openai import OpenAI
import json

# 配置参数
CHAT_ID = "a044b8fa3d4c11f08a7af697fdd30179"
API_KEY = "ragflow-FlNDljYzU0M2UxMTExZjA5NGUxMGU0NW"
BASE_URL = "http://localhost:8080"

# 初始化客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=f"{BASE_URL}/api/v1/chats_openai/{CHAT_ID}"
)

def chat_with_ai(messages):
    """与AI进行对话"""
    try:
        completion = client.chat.completions.create(
            model="model",
            messages=messages,
            stream=True
        )
        
        response_content = ""
        print("\nAI: ", end="", flush=True)
        for chunk in completion:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                response_content += content
                print(content, end="", flush=True)
        print("\n")
        return response_content
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return None

def main():
    # 初始化对话历史
    messages = [
        {
            "role": "system",
            "content": """你是规则怪谈世界中的人物，请总结知识库的内容来对相关场景作出反应（可以是行动，回答等反应形式）。
只需要反应（模拟用户的语言方式），不需要原因解释，用户将根据规则对场景进行模拟，你必须做出正确反应。
当所有知识库内容都与问题无关时，你的回答必须包括"知识库中未找到您要的答案！"这句话。
回答需要考虑聊天历史。"""
        }
    ]
    
    print("欢迎来到规则怪谈世界！(输入 'exit' 退出)")
    print("-" * 50)
    
    while True:
        user_input = input("你: ").strip()
        
        if user_input.lower() == 'exit':
            print("再见！")
            break
            
        if not user_input:
            continue
            
        # 添加用户消息到历史
        messages.append({"role": "user", "content": user_input})
        
        # 获取AI响应
        response = chat_with_ai(messages)
        
        if response:
            # 添加AI响应到历史
            messages.append({"role": "assistant", "content": response})
        else:
            print("对话出现错误，请重试。")
            # 移除最后一条用户消息，因为没有得到有效响应
            messages.pop()

if __name__ == "__main__":
    main()