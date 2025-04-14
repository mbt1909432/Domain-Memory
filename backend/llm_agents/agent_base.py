from typing import AsyncGenerator, Dict, Any, Optional
from openai import AsyncOpenAI
from sqlalchemy.sql.functions import random

from utils.config import CONFIG
from llm_agents.agent_log import AgentLog,AgentLogType,AgentMemoryType
from llm_agents.prompts_base import BasePromptTemplate, UserPromptBase
from llm_agents.agent_parser import parser  # 添加对解析器的引用
from llm_agents.agent_utils import get_request_data
from llm_agents.memory_manager import MemoryManager

import random





class AgentBase:
    """Agent 基类，统一处理与 LLM 的交互"""
    
    def __init__(self, agent_name: str, prompts_template: BasePromptTemplate, model: str = None):
        """初始化 Agent
        
        Args:
            agent_name: Agent 名称，用于日志记录
            prompts_template: 提示模板对象
            model: 使用的模型 ID，默认为 None，使用配置中的默认模型
        """
        self._agent_name = agent_name
        self.log = AgentLog(random.randint(0, 1000000), agent_name)
        self._client = AsyncOpenAI(
            api_key=CONFIG.llm_api_key, 
            base_url=CONFIG.llm_base_url,
            default_headers={"x-agent-id": agent_name}
        )
        self.prompts_template = prompts_template
        self._messages = []
        self.memory_manager = MemoryManager()
        # 如果指定了模型，使用指定的模型，否则使用配置中的默认模型
        self.model = model or CONFIG.model
        
        # 记录使用的模型
        self.log.log_agent_details(
            AgentLogType.SYSTEM,
            AgentMemoryType.WITHOUT_MEMORY,
            False,
            f"Agent initialized with model: {self.model}"
        )

    async def generate(
        self, 
        request_model, 
        with_memory: bool = False, 
        memory_list: list = None, 
        keep_memory: int = -1,
        model: str = None
    ) -> Dict[str, str]:
        """生成单次结果
        
        Args:
            request_model: 请求模型对象
            with_memory: 是否使用内存模式
            memory_list: 记忆列表，仅在 with_memory=True 时使用
            keep_memory: 保留的记忆条数，-1表示全部保留
            model: 可选的模型覆盖，如果提供，将覆盖初始化时设置的模型
            
        Returns:
            包含生成结果的字典
        """
        request_data = get_request_data(request_model)
        
        # 使用请求中指定的模型（如果有）
        current_model = model or self.model
        
        # 使用统一的方法调用 LLM
        result = await self._call_llm(
            request_data=request_data,
            with_memory=with_memory,
            memory_list=memory_list,
            keep_memory=keep_memory,
            is_stream=False,
            model=current_model
        )
        
        return result
    
    async def generate_stream(
        self, 
        request_model, 
        with_memory: bool = False, 
        memory_list: list = None, 
        keep_memory: int = -1,
        model: str = None
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式生成结果
        
        Args:
            request_model: 请求模型对象
            with_memory: 是否使用内存模式
            memory_list: 记忆列表，仅在 with_memory=True 时使用
            keep_memory: 保留的记忆条数，-1表示全部保留
            model: 可选的模型覆盖，如果提供，将覆盖初始化时设置的模型
            
        Yields:
            生成结果的流式片段
        """
        request_data = get_request_data(request_model)
        
        # 使用请求中指定的模型（如果有）
        current_model = model or self.model
        
        # 使用统一的方法调用 LLM，但设置流式输出标志
        async for chunk in self._call_llm_stream(
            request_data=request_data,
            with_memory=with_memory,
            memory_list=memory_list,
            keep_memory=keep_memory,
            model=current_model
        ):
            yield chunk
    
    async def _call_llm(
        self, 
        request_data: Dict[str, Any], 
        with_memory: bool = False,
        memory_list: list = None,
        keep_memory: int = -1, 
        is_stream: bool = False,
        model: str = None
    ) -> Dict[str, str]:
        """统一的 LLM 调用方法，处理有记忆和无记忆两种模式
        
        Args:
            model: 要使用的模型，如果为 None 则使用默认模型
        """
        # 确定要使用的模型
        current_model = model or self.model
        
        if with_memory:
            # 内存模式
            if memory_list is None:
                memory_list = []
                
            async for result in self._call_agent_with_memory_internal(
                memory_list,
                is_stream,
                keep_memory,
                model=current_model,
                **request_data
            ):
                # 处理输出中的特殊格式并返回第一个结果
                return self._process_llm_output(result)
        else:
            # 无内存模式
            user_prompt = self.prompts_template.get_format_user_prompt(**request_data)
            
            async for result in self._call_agent_without_memory_internal(
                user_prompt,
                is_stream,
                model=current_model,
                **request_data
            ):
                # 处理输出中的特殊格式并返回第一个结果
                return self._process_llm_output(result)
    
    async def _call_llm_stream(
        self, 
        request_data: Dict[str, Any], 
        with_memory: bool = False,
        memory_list: list = None,
        keep_memory: int = -1,
        model: str = None
    ) -> AsyncGenerator[Dict[str, str], None]:
        """统一的流式 LLM 调用方法
        
        Args:
            model: 要使用的模型，如果为 None 则使用默认模型
        """
        # 确定要使用的模型
        current_model = model or self.model
        
        if with_memory:
            # 内存模式
            if memory_list is None:
                memory_list = []
                
            async for result in self._call_agent_with_memory_internal(
                memory_list,
                True,  # 始终使用流式
                keep_memory,
                model=current_model,
                **request_data
            ):
                # 处理流式块并 yield
                yield self._process_llm_output_stream(result)
        else:
            # 无内存模式
            user_prompt = self.prompts_template.get_format_user_prompt(**request_data)
            
            async for result in self._call_agent_without_memory_internal(
                user_prompt,
                True,  # 始终使用流式
                model=current_model,
                **request_data
            ):
                # 处理流式块并 yield
                yield self._process_llm_output_stream(result)
    
    def _process_llm_output(self, result: Dict[str, str]) -> Dict[str, str]:
        """处理 LLM 输出，解析特殊格式"""
        if '::' in result["message"]:
            parsed_content = parser(result["message"])
            if parsed_content:
                result["message"] = parsed_content
                result["content"] = parsed_content
        return result
    
    def _process_llm_output_stream(self, result: Dict[str, str]) -> Dict[str, str]:
        """处理流式 LLM 输出，解析特殊格式"""
        if '::' in result["content"]:
            parsed_content = parser(result["content"])
            if parsed_content:
                result["content"] = parsed_content
        return result
    
    async def _call_agent_without_memory_internal(self, user_query: str, is_stream: bool, model: str = None, **kwargs):
        """内部方法：无记忆模式调用 LLM
        
        Args:
            model: 要使用的模型，如果为 None 则使用默认模型
        """
        try:
            # 确定要使用的模型
            current_model = model or self.model
            
            # 重构后的方法，移除重复代码
            self._messages.clear()
            
            # 格式化系统提示
            system = self.prompts_template.get_format_system_prompt(**kwargs)
            self.log.log_agent_details(AgentLogType.SYSTEM, AgentMemoryType.WITHOUT_MEMORY, is_stream, system)
            
            # 设置消息列表
            self._messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user_query}
            ]
            
            # 记录用户查询
            self.log.log_agent_details(AgentLogType.USER, AgentMemoryType.WITHOUT_MEMORY, is_stream, user_query)
            
            # 记录使用的模型
            self.log.log_agent_details(
                AgentLogType.SYSTEM, 
                AgentMemoryType.WITHOUT_MEMORY, 
                is_stream, 
                f"Using model: {current_model}"
            )
            
            # 记录发送到API的消息
            self.log.log_agent_details(
                AgentLogType.SYSTEM,
                AgentMemoryType.WITHOUT_MEMORY,
                is_stream,
                f"Sending messages to API: {self._messages}"
            )
            
            # 调用 LLM API
            try:
                response = await self._client.chat.completions.create(
                    model=current_model,  # 使用指定的模型
                    messages=self._messages,
                    stream=is_stream
                )
                
                # 记录原始API响应
                self.log.log_agent_details(
                    AgentLogType.SYSTEM,
                    AgentMemoryType.WITHOUT_MEMORY,
                    is_stream,
                    f"Raw API response: {response}"
                )
                
            except Exception as api_error:
                self.log.log_agent_error(f"API call failed: {str(api_error)}")
                yield {"message": f"Error: API call failed - {str(api_error)}"}
                return
            
            # 处理响应
            async for result in self._process_response(response, is_stream, AgentMemoryType.WITHOUT_MEMORY):
                yield result
            
        except Exception as e:
            self.log.log_agent_error(f"Error in _call_agent_without_memory_internal: {str(e)}")
            yield {"message": f"Error in agent call: {str(e)}"}
    
    async def _call_agent_with_memory_internal(self, memory_list: list, is_stream: bool, keep_memory: int = -1, model: str = None, **kwargs):
        """内部方法：有记忆模式调用 LLM
        
        Args:
            model: 要使用的模型，如果为 None 则使用默认模型
        """
        # 确定要使用的模型
        current_model = model or self.model
        
        # 重构后的方法，移除重复代码
        self._messages.clear()
        
        # 格式化系统提示
        system = self.prompts_template.get_format_system_prompt(**kwargs)
        self.log.log_agent_details(AgentLogType.SYSTEM, AgentMemoryType.WITH_MEMORY, is_stream, system)
        
        # 设置消息列表
        self._messages.append({"role": "system", "content": system})
        self._messages.extend(memory_list)
        
        # 裁剪记忆
        if 1 <= keep_memory < len(self._messages):
            self._messages = [self._messages[0]] + self._messages[-keep_memory:]
        
        # 记录完整消息列表
        self.log.log_agent_details(AgentLogType.USER, AgentMemoryType.WITH_MEMORY, is_stream, str(self._messages))
        
        # 记录使用的模型
        self.log.log_agent_details(
            AgentLogType.SYSTEM, 
            AgentMemoryType.WITH_MEMORY, 
            is_stream, 
            f"Using model: {current_model}"
        )
        
        # 调用 LLM API
        response = await self._client.chat.completions.create(
            model=current_model,  # 使用指定的模型
            messages=self._messages,
            stream=is_stream
        )
        
        # 处理响应
        async for result in self._process_response(response, is_stream, AgentMemoryType.WITH_MEMORY):
            yield result
    
    async def _process_response(self, response, is_stream: bool, memory_type: AgentMemoryType):
        """Process the response from LLM API call.
        
        Args:
            response: The raw response from LLM API
            is_stream: Whether the response is streaming
            memory_type: Type of memory to use
            
        Yields:
            Processed response message
        """
        try:
            if response is None:
                self.log.log_agent_error("Received None response from LLM API")
                yield {"message": "Error: API returned no response"}
                return

            # Check for API error in response
            if hasattr(response, 'error'):
                error_msg = response.error.get('message', 'Unknown API error')
                error_code = response.error.get('code', 'unknown')
                self.log.log_agent_error(f"API error: {error_msg} (code: {error_code})")
                yield {"message": f"Error: API error - {error_msg}"}
                return

            # Log the response type and structure
            self.log.log_agent_details(
                AgentLogType.SYSTEM,
                memory_type,
                is_stream,
                f"Response type: {type(response)}, Response structure: {dir(response)}"
            )

            if not hasattr(response, 'choices'):
                self.log.log_agent_error(f"Response missing choices attribute: {response}")
                yield {"message": "Error: Response missing choices"}
                return
            
            if not response.choices:
                # Check if there's an error field in the response
                if hasattr(response, 'error'):
                    error_msg = response.error.get('message', 'Unknown error')
                    self.log.log_agent_error(f"API error in response: {error_msg}")
                    yield {"message": f"Error: API error - {error_msg}"}
                else:
                    self.log.log_agent_error("Response choices is empty")
                    yield {"message": "Error: Empty response choices"}
                return

            # Log the first choice structure
            self.log.log_agent_details(
                AgentLogType.SYSTEM,
                memory_type,
                is_stream,
                f"First choice type: {type(response.choices[0])}, Structure: {dir(response.choices[0])}"
            )

            if is_stream:
                # Handle streaming response
                try:
                    async for chunk in response:
                        # Check for errors in streaming chunks
                        if hasattr(chunk, 'error'):
                            error_msg = chunk.error.get('message', 'Unknown streaming error')
                            self.log.log_agent_error(f"Streaming error: {error_msg}")
                            yield {"message": f"Error: Streaming error - {error_msg}"}
                            return
                            
                        if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                            content = chunk.choices[0].delta.content
                            if content:
                                if memory_type == AgentMemoryType.WITH_MEMORY:
                                    self.memory_manager.add_message("assistant", content)
                                yield {"message": content, "content": content}
                except Exception as stream_error:
                    self.log.log_agent_error(f"Error processing stream: {str(stream_error)}")
                    yield {"message": f"Error processing stream: {str(stream_error)}"}
                return

            if not hasattr(response.choices[0], 'message'):
                self.log.log_agent_error(f"Response missing message field: {response.choices[0]}")
                yield {"message": "Error: Response missing message"}
                return

            if not hasattr(response.choices[0].message, 'content'):
                self.log.log_agent_error(f"Message missing content field: {response.choices[0].message}")
                yield {"message": "Error: Message missing content"}
                return

            # Now we can safely access the content
            result = response.choices[0].message.content
            
            if memory_type == AgentMemoryType.WITH_MEMORY:
                # Store response in memory if using memory
                self.memory_manager.add_message("assistant", result)
            
            yield {"message": result}
            
        except Exception as e:
            self.log.log_agent_error(f"Error processing LLM response: {str(e)}")
            yield {"message": f"Error processing response: {str(e)}"}

    async def chat(self, user_input: str, system_params: Dict[str, Any] = None, model: str = None) -> Dict[str, str]:
        """简化的聊天接口，自动管理记忆
        
        Args:
            user_input: 用户输入文本
            system_params: 系统参数，用于格式化系统提示
            model: 要使用的模型，如果为 None 则使用默认模型
        """
        self.memory_manager.add_message("user", user_input)
        memory_list = self.memory_manager.get_messages()
        
        if system_params is None:
            system_params = {}
        
        # 确定要使用的模型
        current_model = model or self.model
        
        # 使用核心 LLM 调用方法
        result = await self._call_llm(
            request_data=system_params,
            with_memory=True,
            memory_list=memory_list,
            keep_memory=-1,
            is_stream=False,
            model=current_model
        )
        
        self.memory_manager.add_message("assistant", result["message"])
        return result


if __name__=="__main__":
    pass

