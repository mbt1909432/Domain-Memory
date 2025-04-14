"""Agent 实用工具函数"""
from typing import Dict, Any, Optional
import json
import re
from utils.config import LOG

def get_request_data(request_model) -> Dict[str, Any]:
    """统一获取请求模型数据
    
    处理顺序:
    1. 如果对象有 get_data() 方法，调用该方法
    2. 如果对象有 model_dump() 方法 (Pydantic v2)，调用该方法
    3. 如果对象有 dict() 方法 (Pydantic v1)，调用该方法
    4. 如果对象是字典类型，直接返回
    5. 否则，尝试将对象转换为字典
    
    Args:
        request_model: 请求模型对象或字典
        
    Returns:
        模型数据字典
    """
    if hasattr(request_model, 'get_data') and callable(getattr(request_model, 'get_data')):
        return request_model.get_data()
    elif hasattr(request_model, 'model_dump') and callable(getattr(request_model, 'model_dump')):
        return request_model.model_dump()
    elif hasattr(request_model, 'dict') and callable(getattr(request_model, 'dict')):
        return request_model.dict()
    elif isinstance(request_model, dict):
        return request_model
    else:
        # 尝试转换为字典，如果失败则返回空字典
        try:
            return dict(request_model)
        except (TypeError, ValueError):
            return {}

def extract_json_from_llm_output(text: str) -> Optional[Dict[str, Any]]:
    """从 LLM 输出中提取 JSON
    
    Args:
        text: LLM 输出的文本
        
    Returns:
        解析后的 JSON 字典，失败则返回 None
    """
    try:
        # 尝试直接解析整个文本
        return json.loads(text)
    except json.JSONDecodeError:
        # 如果直接解析失败，尝试使用正则表达式提取 JSON 部分
        json_pattern = r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}'
        match = re.search(json_pattern, text)
        
        if match:
            try:
                json_str = match.group(1) if match.group(1) else match.group(0)
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError) as e:
                LOG.error(f"JSON 提取和解析失败: {str(e)}")
                return None
        
        LOG.error("无法从输出中提取 JSON")
        return None

async def extract_json_with_retry(agent, request_model, model=None, max_retries=2) -> Optional[Dict[str, Any]]:
    """使用重试机制从 LLM 输出中提取 JSON
    
    如果第一次输出不是有效的 JSON，会重新向 LLM 发送请求，
    明确要求返回 JSON 格式的输出。
    
    Args:
        agent: Agent 实例
        request_model: 原始请求模型
        model: 可选的模型 ID
        max_retries: 最大重试次数
        
    Returns:
        解析后的 JSON 字典或 None
    """
    # 第一次尝试
    result = await agent.generate(request_model, model=model)
    llm_output = result.get("message", "")
    parsed_json = extract_json_from_llm_output(llm_output)
    
    retries = 0
    original_text = None
    
    # 获取原始文本
    if hasattr(request_model, 'text'):
        original_text = request_model.text
    elif hasattr(request_model, 'get_data'):
        data = request_model.get_data()
        original_text = data.get('text', '')
    
    # 如果解析失败且有原始文本，尝试重试
    while parsed_json is None and retries < max_retries and original_text:
        LOG.warning(f"JSON 解析失败，尝试重新生成 (尝试 {retries+1}/{max_retries})")
        
        # 创建一个要求返回 JSON 的提示
        retry_message = f"""
您之前的回答无法解析为有效的 JSON 格式。

请重新分析以下参考文献，并以严格的 JSON 格式返回结果，格式如下：
```json
{{
  "authors": "作者名，多个作者以分号分隔",
  "year": "出版年份",
  "title": "文章标题",
  "journal": "期刊名称",
  "volume": "卷号",
  "pages": "页码范围"
}}
```

不要在 JSON 外包含任何额外文本或解释。确保所有字段值都是字符串类型。如果无法提取某个字段，将其值设为空字符串。

参考文献: {original_text}
"""
        
        # 创建新的请求
        from schemas.agents.reference_schema import ReferenceParseRequest
        retry_request = ReferenceParseRequest(text=retry_message)
        
        # 重新生成
        LOG.info(f"重新请求 LLM 生成 JSON 格式输出, 重试次数: {retries+1}")
        result = await agent.generate(retry_request, model=model)
        llm_output = result.get("message", "")
        
        # 尝试解析
        parsed_json = extract_json_from_llm_output(llm_output)
        retries += 1
    
    if parsed_json is None:
        LOG.error(f"经过 {max_retries} 次重试后仍无法获取有效的 JSON 输出")
    else:
        LOG.info(f"成功获取 JSON 输出，重试次数: {retries}")
        
    return parsed_json 