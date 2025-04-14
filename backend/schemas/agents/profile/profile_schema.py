from enum import StrEnum
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class OpenAICompatibleMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    alias: Optional[str] = None
    created_at: Optional[str] = None


class ChatBlob(BaseModel):
    "用户和聊天机器人的对话"
    messages: list[OpenAICompatibleMessage]


class ProfileSummary(BaseModel):
    "用户总结信息"
    summary:str


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    system_prompt: Optional[str] = Field(None, description="可选的系统提示")

    def get_data(self) -> Dict[str, Any]:
        """获取数据字典"""
        data = {
            "message": self.message
        }
        if self.system_prompt:
            data["system_prompt"] = self.system_prompt
        return data


class UserProfile(BaseModel):
    domain: str = Field(..., description="个人资料的领域，如basic_info, work, contact_info等")
    attribute: str = Field(..., description="该领域下的具体属性，如Age, profession, city等")
    description: str = Field(..., description="属性的具体描述内容")


class UserProfiles(BaseModel):
    facts: List[UserProfile] = Field(..., description="用户资料事实列表")
    
    def __len__(self):
        """返回facts列表的长度，使对象可以直接用于len()函数"""
        return len(self.facts)


class ProfileUpdateInput(BaseModel):
    """用于更新用户资料的输入参数模型"""
    domain: str = Field(..., description="个人资料的领域，如basic_info, work, interest等")
    attribute: str = Field(..., description="该领域下的具体属性，如age, profession, hobby等")
    old_description: str = Field(..., description="现有的资料描述")
    new_description: str = Field(..., description="新的资料描述")


class ProfileUpdateResult(BaseModel):
    """用户资料更新结果模型"""
    action: Literal["UPDATE", "MERGE", "KEEP"] = Field(..., description="执行的操作类型")
    description: str = Field(..., description="更新后的资料描述")
    domain: str = Field(..., description="个人资料的领域")
    attribute: str = Field(..., description="该领域下的具体属性")



class ProfileProcessResult(BaseModel):
    """用户资料处理结果模型"""
    extracted_profiles: UserProfiles = Field(
        default_factory=lambda: UserProfiles(facts=[]),
        description="从聊天中提取的新资料信息"
    )
    updates: List[ProfileUpdateResult] = Field(
        default_factory=list,
        description="更新的资料信息"
    )
    organized_profiles: UserProfiles = Field(
        default_factory=lambda: UserProfiles(facts=[]),
        description="组织后的资料信息"
    )
    profile_summary: str = Field(
        default="",
        description="资料的总体摘要"
    )
    status: Literal["success", "warning", "error"] = Field(
        default="success",
        description="处理状态"
    )
    message: Optional[str] = Field(
        default=None,
        description="状态消息，通常在warning或error状态下提供"
    )


