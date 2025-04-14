from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class MemoryManager:
    """记忆管理器，处理对话历史"""
    
    def __init__(self, max_tokens: int = 4000):
        self.messages: List[Message] = []
        self.max_tokens = max_tokens
        
    def add_message(self, role: str, content: str) -> None:
        """添加消息到历史"""
        self.messages.append(Message(role=role, content=content))
        self._trim_if_needed()
        
    def get_messages(self) -> List[Dict[str, str]]:
        """获取消息历史"""
        return [msg.model_dump() for msg in self.messages]
    
    def clear(self) -> None:
        """清空历史"""
        self.messages = []
    
    def _trim_if_needed(self) -> None:
        """如果历史过长，裁剪历史"""
        # 简单实现：保留最近的消息
        if len(self.messages) > 20:  # 可以根据token计算更精确的裁剪
            # 保留system消息和最近的消息
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            recent_messages = self.messages[-10:]
            self.messages = system_messages + recent_messages 