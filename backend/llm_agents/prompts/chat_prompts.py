from llm_agents.prompts_base import BasePromptTemplate

class ChatPrompts(BasePromptTemplate):
    """基本的聊天提示模板"""
    
    def __init__(self):
        super().__init__()
        
        self.prefix = """
你是一个智能助手，能够提供有用、安全、准确的回答。请根据用户的提问提供帮助。

${system_prompt}
"""
        
        self.examples = []
        
        self.suffix = """
请以简洁、专业的方式回答，提供有价值的信息。
"""
        
        self.user_prompt = """
${message}
""" 