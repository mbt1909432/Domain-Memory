from typing import Dict, Any, Optional, List
from string import Template

from pydantic import BaseModel, Field
from  enum import Enum
from utils.config import LOG

def substitute_example():
    # 定义模板和参数
    # substitute 只要文本里有占位符就必须被匹配到，否则报错， 传进来多余的占位符不会有影响
    prefix = "Hello, $name! Welcome to ${place}."
    kwargs = {"name": "A", "place": "Python World", 'test': 'test'}

    try:
        # 尝试替换占位符
        formatted_prefix = Template(prefix).substitute(**kwargs) if prefix else ""
        print("替换后的字符串:", formatted_prefix)
    except KeyError as e:
        # 处理缺少占位符的情况
        print(f"错误：缺少占位符 {e}，请检查 kwargs 是否包含所有需要的键。")
    except Exception as e:
        # 处理其他异常
        print(f"发生未知错误：{e}")


class PromptType(Enum):
    """Prompt 类型枚举"""
    PREFIX = "PREFIX"
    EXAMPLE = "EXAMPLE"
    SUFFIX = "SUFFIX"
    USER = "USER"



# 定义 Example 模型
class Example(BaseModel):
    input: str = Field(..., description="示例输入")
    output: str = Field(..., description="示例输出")


class UserPromptBase(BaseModel):
    """用户提示基类"""
    input: str = Field(default="请输入你的用户数据", description="user input")



class BasePromptTemplate:
    """提示模板基类"""
    
    def __init__(self):
        """初始化提示模板"""
        self.prefix = ""
        self.examples: List[Example] = []
        self.suffix = ""
        self.user_prompt = ""
        
    def set_examples_str(self) -> str:
        """格式化示例字符串
        
        Returns:
            格式化后的示例字符串
        """
        if not self.examples:
            return ""
            
        examples_str = "\n\nExamples:\n"
        for i, example in enumerate(self.examples, 1):
            examples_str += f"Example {i}:\n"
            examples_str += f"Input:\n{example.input}\n"
            examples_str += f"Output:\n{example.output}\n\n"
        return examples_str

    def print_prompt_template(self) -> None:
        """打印提示模板"""
        examples_str = self.set_examples_str()
        
        print("======== SYSTEM PROMPT ========")
        print(self.prefix + examples_str + self.suffix)
        print("======== USER PROMPT ========")
        print(self.user_prompt)
        print("==============================")

    def _format_prompt(self, prompt: str, prompt_type: PromptType, **kwargs) -> Optional[str]:
        """格式化提示
        
        Args:
            prompt: 提示字符串
            prompt_type: 提示类型
            kwargs: 格式化参数
            
        Returns:
            格式化后的提示字符串，失败时返回 None
        """
        if not prompt:
            return ""
            
        try:
            return Template(prompt).substitute(**kwargs)
        except KeyError as e:
            # 记录缺少的占位符
            LOG.error(f"错误：缺少占位符 {e}，请检查 {prompt_type.value} 是否包含所有需要的键。")
            return None
        except Exception as e:
            # 处理其他异常
            LOG.error(f"格式化 {prompt_type.value} 时发生错误: {e}")
            return None

    def get_format_system_prompt(self, **kwargs) -> str:
        """获取格式化的系统提示
        
        Args:
            kwargs: 格式化参数
            
        Returns:
            格式化后的系统提示
        """
        formatted_prefix = self._format_prompt(self.prefix, PromptType.PREFIX, **kwargs) or ""
        formatted_suffix = self._format_prompt(self.suffix, PromptType.SUFFIX, **kwargs) or ""
        examples_str = self.set_examples_str()
        
        # 组合完整的系统提示
        result = formatted_prefix + examples_str + formatted_suffix
        
        if not result:
            LOG.warning("系统提示为空，请检查模板配置")
            return "系统提示配置错误，请联系管理员"
            
        return result

    def get_format_user_prompt(self, **kwargs) -> str:
        """获取格式化的用户提示
        
        Args:
            kwargs: 格式化参数
            
        Returns:
            格式化后的用户提示
        """
        formatted_user = self._format_prompt(self.user_prompt, PromptType.USER, **kwargs) or ""
        
        if not formatted_user and self.user_prompt:
            LOG.warning("用户提示格式化失败，使用默认提示")
            return "请输入您的请求"
            
        return formatted_user


class examplePrompt(BasePromptTemplate):
    """prompt模板参考"""
    def __init__(self):
        super().__init__()

        self.prefix = """prefix 例子 ${data}"""

        self.examples=[Example(input="input",output="output")]


        self.suffix = """suffix"""


        self.user_prompt = """## 用户输入
### 原文
${input}
### 缩写后的文本"""



def main():
    """正确用法"""
    print("---------正确用法-----------")
    a=examplePrompt()
    print(a.get_format_system_prompt(**{"data":"data"}))
    print(a.get_format_user_prompt(**UserPromptBase(input="你好啊").model_dump()))

def main2():
    """正确用法"""
    print("---------错误用法，参数校验-----------")
    a=examplePrompt()
    print(a.get_format_system_prompt())
    print(a.get_format_user_prompt(**UserPromptBase(input="你好啊").model_dump()))

def main3():
    """多轮动态模板清除"""
    print("---------多轮动态模板清除-----------")
    print("---------round1-----------")
    a=examplePrompt()
    print(a.get_format_system_prompt(**{"data":"data1"}))
    print(a.get_format_user_prompt(**UserPromptBase(input="嘿嘿").model_dump()))
    print("---------round2-----------")
    print(a.get_format_system_prompt(**{"data":"data2"}))
    print(a.get_format_user_prompt(**UserPromptBase(input="你好啊").model_dump()))


if __name__ == "__main__":
    #main()
    #main2()
    main3()
