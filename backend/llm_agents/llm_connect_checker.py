import asyncio
import time
from typing import Dict, Union
from openai import AsyncOpenAI, APIConnectionError, AuthenticationError, RateLimitError, APIError
from openai.types.chat import ChatCompletion
from utils.config import CONFIG
from utils.config import LOG


async def llm_connect_test(timeout: int = 10) -> Dict[str, Union[bool, str, float]]:
    """
    异步测试LLM服务连通性

    :param timeout: 请求超时时间（秒），默认10秒
    :return: 包含测试结果的字典
    """
    result = {
        "success": False,
        "message": "Initializing",
        "latency": 0.0,
        "model": CONFIG.model,
        "error_type": None,
        "error_detail": None
    }

    start_time = time.time()

    try:
        # 初始化异步客户端
        client = AsyncOpenAI(
            api_key=CONFIG.llm_api_key,
            base_url=CONFIG.llm_base_url,
            timeout=timeout,
            max_retries=2,
            default_headers={"X-Test-Request": "connectivity-check"}
        )

        LOG.info(f"开始异步LLM连通性测试 | 模型: {CONFIG.model}")

        # 异步请求
        response: ChatCompletion = await client.chat.completions.create(
            model=CONFIG.model,
            messages=[
                {"role": "system", "content": "连通性测试，请直接回复'OK'"},
                {"role": "user", "content": "PING"},
            ],
            stream=False,
            temperature=0.0,
            max_tokens=5
        )

        # 处理响应
        reply = response.choices[0].message.content.strip()

        # 记录成功结果
        result.update({
            "success": True,
            "message": "Success",
            "latency": round(time.time() - start_time, 3)
        })
        LOG.info(f"异步连接LLM测试成功 | 延迟: {result['latency']}s | LLM输出结果为 {reply}")

    except APIConnectionError as e:
        error_detail = f"{e.__class__.__name__}: {e.message}"
        result.update({
            "message": "API连接失败",
            "error_type": "ConnectionError",
            "error_detail": error_detail
        })
        LOG.error(f"连接异常 | 详情: {error_detail}")
    except AuthenticationError as e:
        result.update({
            "message": "认证失败",
            "error_type": "AuthError",
            "error_detail": str(e)
        })
        LOG.error("API密钥无效 | 请检查配置")
    except RateLimitError as e:
        result.update({
            "message": "请求限速",
            "error_type": "RateLimit",
            "error_detail": str(e)
        })
        LOG.warning("速率超限 | 建议调整请求频率")
    except APIError as e:
        result.update({
            "message": f"API错误: {e.code}",
            "error_type": "APIError",
            "error_detail": str(e)
        })
        LOG.error(f"服务端异常 | 状态码: {e.code}")
    except Exception as e:
        result.update({
            "message": "未知错误",
            "error_type": "UnknownError",
            "error_detail": str(e)
        })
        LOG.error(f"未捕获异常 | 类型: {type(e)}")
    finally:
        # 确保延迟计算
        if result["latency"] == 0:
            result["latency"] = round(time.time() - start_time, 3)

        # 生成最终状态
        if not result["success"]:
            result["message"] = f"失败: {result['message']}"

        return result


if __name__ == "__main__":
    # 异步执行测试
    test_result = asyncio.run(llm_connect_test())
    print("测试结果:", test_result)