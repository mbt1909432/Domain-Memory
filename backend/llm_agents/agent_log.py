"""增强的 Agent 日志系统"""
import logging
from enum import Enum
from datetime import datetime
import traceback

from rich.logging import RichHandler
from utils.config import LOGS_DIR

class AgentLogType(Enum):
    """Agent 日志类型"""
    SYSTEM = 'SYSTEM'
    USER = 'USER'
    LLM_OUTPUT = 'LLM_OUTPUT'
    ERROR = 'ERROR'
    TIMING = 'TIMING'

class AgentMemoryType(Enum):
    """Agent 内存类型"""
    WITH_MEMORY = 'WITH_MEMORY'
    WITHOUT_MEMORY = 'WITHOUT_MEMORY'

# 配置日志
AGENT_LOG = logging.getLogger("agent_system")
AGENT_LOG.setLevel(logging.INFO)

# 控制台处理器
console_handler = RichHandler(rich_tracebacks=True)
AGENT_LOG.addHandler(console_handler)

# 文件处理器
file_handler = logging.FileHandler(LOGS_DIR / "agent.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
AGENT_LOG.addHandler(file_handler)

class AgentLog:
    """Agent 日志记录器"""
    
    def __init__(self, agent_seed: int, agent_name: str):
        """初始化日志记录器
        
        Args:
            agent_seed: Agent 种子，用于追踪单个实例
            agent_name: Agent 名称
        """
        self._agent_seed = agent_seed
        self._agent_name = agent_name
        self._start_time = datetime.now()
        
        # 记录初始化日志
        AGENT_LOG.info(
            f"Agent '{agent_name}' initialized with seed {agent_seed} "
            f"at {self._start_time.isoformat()}"
        )

    def log_agent_details(
        self,
        agent_log_type: AgentLogType,
        memory_type: AgentMemoryType,
        is_stream: bool,
        prompt: str,
        logger: logging.Logger = AGENT_LOG,
        log_level: int = logging.INFO,
    ) -> None:
        """记录 Agent 详细信息
        
        Args:
            agent_log_type: 日志类型
            memory_type: 内存类型
            is_stream: 是否流式
            prompt: 提示内容
            logger: 日志记录器
            log_level: 日志级别
        """
        log_message = (
            f"==== {agent_log_type.value} | {self._agent_name} ====\n"
            f"Seed: {self._agent_seed} | 模式: {memory_type.value} | 流式: {is_stream}\n"
            f"内容: {prompt[:200]}{'...' if len(prompt) > 200 else ''}\n"
            f"==== 结束 {agent_log_type.value} ===="
        )
        logger.log(log_level, log_message)
        
    def log_agent_error(self, error_message: str) -> None:
        """记录 Agent 错误
        
        Args:
            error_message: 错误信息
        """
        log_message = (
            f"!!!! ERROR | {self._agent_name} !!!!\n"
            f"Seed: {self._agent_seed}\n"
            f"Error: {error_message}\n"
            f"Trace: {traceback.format_exc()}\n"
            f"!!!! 结束 ERROR !!!!"
        )
        AGENT_LOG.error(log_message)
        
    def log_timing(self, operation_name: str) -> None:
        """记录操作时间
        
        Args:
            operation_name: 操作名称
        """
        now = datetime.now()
        elapsed = now - self._start_time
        log_message = (
            f"---- TIMING | {self._agent_name} ----\n"
            f"Seed: {self._agent_seed} | 操作: {operation_name}\n"
            f"时长: {elapsed.total_seconds():.2f}秒\n"
            f"---- 结束 TIMING ----"
        )
        AGENT_LOG.info(log_message)

"""
语言模型日志系统我感觉得用时间来，每次创建一个实例就得搞个文件夹，然后里面去做分类不然很乱啊
"""




