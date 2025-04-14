

from pydantic import BaseModel, Field


class UserPrompt(BaseModel):
    """约束用户输入"""
    input:str=Field(...,description="用户prompt约束为input，规范"),

""" Response Model Data """
class AgentResponseData(BaseModel):
    message:str=Field(...,description="完整输出"),
    content:str=Field(...,description="流式局部输出")

