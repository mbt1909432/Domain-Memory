from enum import Enum

from llm_agents.agent_base import AgentBase
from utils.config import PROMPTS_DIR
from llm_agents.prompts_base import BasePromptTemplate
from llm_agents.prompts import literature_review_prompts,outline_helper_prompts,paraphase_prompts


# 定义 prompts 目录的根路径
# TODO:这里加入agent type
# 定义枚举类
class AgentType(Enum):
    PARAPHASE = ("paraphase_agent", paraphase_prompts.ParaphasePrompts())
    EXPAND = ("paraphase_expand_agent", paraphase_prompts.RewritePromptsLong())
    SHORTEN = ("paraphase_shorten_agent", paraphase_prompts.RewritePromptsShort())



# 创建 AgentBase 实例
def create_agent(agent_type:AgentType):
    return AgentBase(agent_type.value[0], agent_type.value[1])


# 示例：使用枚举类创建 AgentBase 实例
if __name__ == "__main__":
    pass

