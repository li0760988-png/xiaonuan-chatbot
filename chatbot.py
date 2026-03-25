import requests
import json
import threading
import time
from config import DEEPSEEK_API_KEY, SYSTEM_PROMPT, API_URL

class Chatbot:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.waiting_for_response = False
        self.timer = None
        self.running = True
    
    def send_message(self, user_message):
        """发送消息并获取 AI 回复"""
        # 取消之前的定时器
        self.cancel_timer()
        
        self.messages.append({"role": "user", "content": user_message})
        
        data = {
            "model": "deepseek-chat",
            "messages": self.messages,
            "temperature": 0.8,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(API_URL, headers=self.headers, json=data)
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                self.messages.append({"role": "assistant", "content": ai_response})
                # AI 回复后，启动定时器，等待用户回复
                self.start_timer()
                return ai_response
            else:
                return f"错误：{response.status_code} - {response.text}"
                
        except Exception as e:
            return f"网络错误：{str(e)}"
    
    def send_proactive_message(self):
        """主动发送消息（当用户长时间未回复时）"""
        # 如果程序已停止，不再发送
        if not self.running:
            return
        
        # 如果正在等待用户回复，发送主动消息
        if self.waiting_for_response:
            print("\n[系统] 小暖看你一直没说话，主动发来消息：")
            
            # 主动提问的消息
            proactive_prompts = [
                "嘿，还在吗？今天过得怎么样呀？",
                "我看你一直没说话，是不是在忙呀？要注意休息哦～",
                "在干嘛呢？有什么想和我聊聊的吗？",
                "今天有什么开心的事想分享吗？",
                "最近有在看什么好看的电影或书吗？"
            ]
            import random
            proactive_message = random.choice(proactive_prompts)
            
            # 把主动消息添加到对话历史（作为 AI 的消息）
            self.messages.append({"role": "assistant", "content": proactive_message})
            print(f"小暖：{proactive_message}")
            
            # 重新启动定时器
            self.start_timer()
    
    def start_timer(self):
        """启动定时器，60秒后如果用户没回复，就主动提问"""
        self.waiting_for_response = True
        self.timer = threading.Timer(60.0, self.send_proactive_message)
        self.timer.start()
    
    def cancel_timer(self):
        """取消定时器（用户回复时调用）"""
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
        self.waiting_for_response = False
    
    def clear_history(self):
        """清空对话历史"""
        self.cancel_timer()
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.waiting_for_response = False
    
    def stop(self):
        """停止程序时调用"""
        self.running = False
        self.cancel_timer()

if __name__ == "__main__":
    bot = Chatbot()
    print("=" * 50)
    print("你好！我是小暖，你的聊天伙伴。")
    print("输入 'quit' 退出，输入 'clear' 清空历史")
    print("如果你1分钟不回复，我会主动找你聊天～")
    print("=" * 50)
    
    try:
        while True:
            user_input = input("\n你：")
            
            if user_input.lower() == 'quit':
                print("再见！记得照顾好自己～")
                break
            elif user_input.lower() == 'clear':
                bot.clear_history()
                print("对话历史已清空")
                continue
            elif user_input == "":
                continue
                
            response = bot.send_message(user_input)
            print(f"小暖：{response}")
    
    except KeyboardInterrupt:
        print("\n\n再见！")
    finally:
        bot.stop()