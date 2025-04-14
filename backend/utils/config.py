import dataclasses
import logging
import os
from dataclasses import dataclass,field
from pathlib import Path
from typing import Dict, List, Any, Optional,Union,Literal
from uuid import uuid4

import yaml
from dotenv import load_dotenv
from rich.logging import RichHandler
import tiktoken



"""
1.项目路径配置
"""
# project root
BASE_DIR = Path(__file__).resolve().parent.parent







def create_dir_from_base(path: str):
    """
    从后端根路径创建目录
    :param path:
    :return:
    """
    DIR = BASE_DIR / path
    DIR.mkdir(exist_ok=True)
    return DIR


DATA_DIR = create_dir_from_base("data")
LOGS_DIR = create_dir_from_base("data/logs")
PROMPTS_DIR = create_dir_from_base("data/prompts")
ENVIRONMENTS_DIR = create_dir_from_base("data/environments")

"""2.env配置用于docker以及此python工程"""
load_dotenv(ENVIRONMENTS_DIR / "project.env")
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")


"""3项目流程配置"""

# 环境目录路径
ENV_DIR = Path(__file__).parent.parent / "data" / "environments"

class Config:
    """应用配置类，用于管理应用程序配置"""
    
    def __init__(self):
        """初始化配置"""
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载配置"""
        self.llm_base_url = ""
        self.llm_api_key = ""
        self.model = "gpt-4o-mini"  # 默认模型
        self.available_models = []

        # 尝试加载配置文件
        yaml_path = ENV_DIR / "project.yaml"
        if yaml_path.exists():
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f)
                    
                    # 加载基本配置
                    self.llm_base_url = yaml_config.get("llm_base_url", "")
                    self.llm_api_key = yaml_config.get("llm_api_key", "")
                    
                    # 加载可用模型
                    if "available_models" in yaml_config and isinstance(yaml_config["available_models"], list):
                        self.available_models = yaml_config["available_models"]
                        
                        # 验证模型配置
                        valid_models = []
                        has_default = False
                        
                        for model in self.available_models:
                            if all(k in model for k in ["model_id", "name", "description"]):
                                valid_models.append(model)
                                if model.get("default", False):
                                    has_default = True
                                    self.model = model["model_id"]
                        
                        self.available_models = valid_models
                        
                        # 如果没有标记默认模型，将第一个设为默认
                        if not has_default and self.available_models:
                            self.available_models[0]["default"] = True
                            self.model = self.available_models[0]["model_id"]
                    
                    # 如果没有有效模型，添加默认模型
                    if not self.available_models:
                        self.available_models = [
                            {
                                "model_id": self.model,
                                "name": self.model,
                                "description": "默认模型",
                                "default": True
                            }
                        ]
            except Exception as e:
                LOG.error(f"加载YAML配置文件时出错: {e}")
                # 设置默认配置
                self._set_default_models()
        else:
            # 如果YAML文件不存在，设置默认配置
            self._set_default_models()
    
    def _set_default_models(self):
        """设置默认模型配置"""
        self.available_models = [
            {
                "model_id": self.model,
                "name": self.model,
                "description": "默认模型",
                "default": True
            }
        ]
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        for model in self.available_models:
            if model.get("default", False):
                return model["model_id"]
        return self.model
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        return self.available_models
    
    def is_model_available(self, model_id: str) -> bool:
        """检查模型是否可用"""
        if not model_id:
            return False
        return any(m["model_id"] == model_id for m in self.available_models)
    
    def get_model_by_id(self, model_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取模型配置
        
        Args:
            model_id: 模型ID
            
        Returns:
            模型配置字典，如果找不到则返回None
        """
        for model in self.available_models:
            if model["model_id"] == model_id:
                return model
        return None



"""4log系统"""

# 配置日志
LOG = logging.getLogger("research_platform_server")
LOG.setLevel(logging.INFO)

# 控制台处理器
console_handler = RichHandler()
LOG.addHandler(console_handler)

# 文件处理器
file_handler = logging.FileHandler(LOGS_DIR / "project.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
LOG.addHandler(file_handler)


LOG.info(f"Database URL: {DATABASE_URL}")
LOG.info(f"Redis URL: {REDIS_URL}")

# 创建全局配置实例
CONFIG = Config()


#Add encoder for tokenize strings
ENCODER = tiktoken.encoding_for_model("gpt-4o")

if __name__ == "__main__":
    print("---test---")
