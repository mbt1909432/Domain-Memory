"""提供统一的 Agent 创建工厂函数"""
from typing import Dict, Any, Type, Optional

from llm_agents.agent_base import AgentBase
from llm_agents.prompts import chat_prompts
from llm_agents.prompts.profile.extract_profile_prompt import Extract_Profile_Prompt
from llm_agents.prompts.profile.update_profile_prompt import Update_Profile_Prompt
from llm_agents.prompts.profile.organize_profile_prompt import Organize_Profile_Prompt
from llm_agents.prompts.profile.summary_profile_prompt import Summary_Profile_Prompt



# 缓存已创建的 agent 实例
# 修改缓存结构：{agent_type}_{model_id} 作为键
_agent_cache = {}

def get_agent_cache_key(base_key: str, model: Optional[str] = None) -> str:
    """获取 Agent 缓存键，根据模型参数生成唯一键
    
    Args:
        base_key: 基础键名
        model: 可选的模型 ID
        
    Returns:
        包含模型信息的缓存键
    """
    if model:
        return f"{base_key}_{model}"
    return base_key

def get_chat_agent(model: str = None) -> AgentBase:
    """获取基础聊天agent
    
    Args:
        model: 可选的模型 ID
    """
    cache_key = get_agent_cache_key("chat_agent", model)
    if cache_key not in _agent_cache:
        prompts = chat_prompts.ChatPrompts()
        agent = AgentBase(cache_key, prompts, model)
        _agent_cache[cache_key] = agent
    return _agent_cache[cache_key]

def get_profile_extraction_agent(model: str = None) -> AgentBase:
    """获取用户资料提取agent
    
    使用专门的提示模板从对话中提取用户资料信息
    
    Args:
        model: 可选的模型 ID
        
    Returns:
        配置为提取用户资料的Agent实例
    """
    cache_key = get_agent_cache_key("profile_extraction_agent", model)
    if cache_key not in _agent_cache:
        prompts = Extract_Profile_Prompt()
        agent = AgentBase(cache_key, prompts, model)
        _agent_cache[cache_key] = agent
    return _agent_cache[cache_key]

def get_profile_update_agent(model: str = None) -> AgentBase:
    """获取用户资料更新agent
    
    使用专门的提示模板来合并和更新用户资料信息
    
    Args:
        model: 可选的模型 ID
        
    Returns:
        配置为更新用户资料的Agent实例
    """
    cache_key = get_agent_cache_key("profile_update_agent", model)
    if cache_key not in _agent_cache:
        prompts = Update_Profile_Prompt()
        agent = AgentBase(cache_key, prompts, model)
        _agent_cache[cache_key] = agent
    return _agent_cache[cache_key]


def get_profile_organize_agent(model: str = None) -> AgentBase:
    """获取用户资料更新agent

    使用专门的提示模板来合并和更新用户资料信息

    Args:
        model: 可选的模型 ID

    Returns:
        配置为更新用户资料的Agent实例
    """
    cache_key = get_agent_cache_key("profile_organize_agent", model)
    if cache_key not in _agent_cache:
        prompts = Organize_Profile_Prompt()
        agent = AgentBase(cache_key, prompts, model)
        _agent_cache[cache_key] = agent
    return _agent_cache[cache_key]

def get_profile_summary_agent(model: str = None) -> AgentBase:
    """获取用户资料更新agent

    使用专门的提示模板来合并和更新用户资料信息

    Args:
        model: 可选的模型 ID

    Returns:
        配置为更新用户资料的Agent实例
    """
    cache_key = get_agent_cache_key("profile_summary_agent", model)
    if cache_key not in _agent_cache:
        prompts = Summary_Profile_Prompt()
        agent = AgentBase(cache_key, prompts, model)
        _agent_cache[cache_key] = agent
    return _agent_cache[cache_key]


