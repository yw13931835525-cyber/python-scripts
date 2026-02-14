#!/usr/bin/env python3
"""
ChatGPT API工具
批量生成/文本处理/对话管理
"""

import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class ChatGPTConfig:
    """ChatGPT配置"""
    api_key: str = ''
    model: str = 'gpt-3.5-turbo'
    max_tokens: int = 2000
    temperature: float = 0.7


class ChatGPT:
    """ChatGPT工具"""
    
    def __init__(self, config: ChatGPTConfig = None):
        self.config = config or ChatGPTConfig()
        
        if not self.config.api_key:
            # 从环境变量读取
            self.config.api_key = os.environ.get('OPENAI_API_KEY', '')
        
        self.client = OpenAI(api_key=self.config.api_key)
        self.conversation_history = []
    
    def ask(self, prompt: str, system_prompt: str = None) -> str:
        """单次对话"""
        messages = []
        
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        messages.append({'role': 'user', 'content': prompt})
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        return response.choices[0].message.content
    
    def chat(self, message: str) -> str:
        """连续对话"""
        self.conversation_history.append({'role': 'user', 'content': message})
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=self.conversation_history,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        reply = response.choices[0].message.content
        self.conversation_history.append({'role': 'assistant', 'content': reply})
        
        return reply
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("对话历史已清空")
    
    def batch_generate(self, prompts: List[str], system_prompt: str = None) -> List[str]:
        """批量生成"""
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                result = self.ask(prompt, system_prompt)
                results.append(result)
                print(f"[{i+1}/{len(prompts)}] 完成")
            except Exception as e:
                results.append(f"Error: {e}")
                print(f"[{i+1}/{len(prompts)}] 失败: {e}")
        
        return results


class ContentGenerator:
    """内容生成器"""
    
    def __init__(self, api_key: str = ''):
        self.gpt = ChatGPT(ChatGPTConfig(api_key=api_key))
    
    def generate_titles(self, topic: str, count: int = 10) -> List[str]:
        """生成标题"""
        prompt = f"为'{topic}'生成{count}个吸引人的标题，每个标题用换行分隔"
        result = self.gpt.ask(prompt, "你是专业的内容创作者")
        
        titles = [t.strip() for t in result.split('\n') if t.strip()]
        return titles[:count]
    
    def generate_descriptions(self, product_name: str, features: List[str], count: int = 5) -> List[str]:
        """生成商品描述"""
        prompt = f"""为'{product_name}'生成{count}个商品描述。
特点: {', '.join(features)}
每个描述100字以内，用换行分隔。"""
        
        result = self.gpt.ask(prompt, "你是专业电商文案")
        
        descriptions = [d.strip() for d in result.split('\n') if d.strip()]
        return descriptions[:count]
    
    def generate_social_posts(self, topic: str, platform: str = 'wechat', count: int = 5) -> List[str]:
        """生成社交媒体帖子"""
        platform_hints = {
            'wechat': '微信公众号风格',
            'weibo': '微博风格，简洁有力',
            'xiaohongshu': '小红书风格，种草文案',
            'zhihu': '知乎风格，专业详细'
        }
        
        prompt = f"用{platform_hints.get(platform, '普通')}为'{topic}'生成{count}条社交媒体帖子"
        result = self.gpt.ask(prompt, "你是社交媒体运营专家")
        
        posts = [p.strip() for p in result.split('\n') if p.strip()]
        return posts[:count]
    
    def summarize_text(self, text: str, length: str = 'medium') -> str:
        """摘要"""
        lengths = {
            'short': '一句话总结',
            'medium': '100字总结',
            'long': '200字总结'
        }
        
        prompt = f"{lengths.get(length, lengths['medium'])}:\n\n{text[:3000]}"
        return self.gpt.ask(prompt, "你是专业编辑")
    
    def translate_text(self, text: str, target: str = 'Chinese') -> str:
        """翻译"""
        prompt = f"将以下文本翻译成{target}，只返回翻译结果:\n\n{text[:2000]}"
        return self.gpt.ask(prompt)


class EmailGenerator:
    """邮件生成器"""
    
    def __init__(self, api_key: str = ''):
        self.gpt = ChatGPT(ChatGPTConfig(api_key=api_key))
    
    def write_email(self, purpose: str, recipient: str, key_points: List[str], tone: str = 'professional') -> str:
        """写信"""
        prompt = f"""写一封{ tone }邮件。
目的: {purpose}
收件人: {recipient}
要点: {', '.join(key_points)}
只返回邮件正文，不包含主题行。"""
        
        return self.gpt.ask(prompt)
    
    def reply_email(self, original_email: str, response_points: List[str]) -> str:
        """回信"""
        prompt = f"""根据原邮件内容，用合适的语气回复。
原邮件:
{original_email}

回复要点:
{', '.join(response_points)}

只返回回复内容。"""
        
        return self.gpt.ask(prompt, "你是专业秘书")


# 示例使用
if __name__ == "__main__":
    # 初始化
    # gpt = ChatGPT(ChatGPTConfig(api_key="your-api-key"))
    
    # 单次对话
    # response = gpt.ask("你好！")
    # print(response)
    
    # 内容生成
    # generator = ContentGenerator()
    # titles = generator.generate_titles("Python编程", 5)
    # for t in titles:
    #     print(f"- {t}")
    
    # 邮件生成
    # email_gen = EmailGenerator()
    # email = email_gen.write_email(
    #     purpose="产品推广",
    #     recipient="客户",
    #     key_points=["新品上线", "限时优惠", "品质保证"]
    # )
    # print(email)
    
    print("ChatGPT工具已就绪！")
