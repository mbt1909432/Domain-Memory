import json
import requests
import os
from datetime import datetime
import openai

# API 配置
OLLAMA_API_ENDPOINT = "http://localhost:11434/api/chat"  # 根据你的 Ollama 部署调整
OLLAMA_MODEL_NAME = "llama3"  # 使用你想要的模型名称，如 llama3, mistral, gemma 等
OPENAI_MODEL_NAME = "gpt-3.5-turbo"  # 默认的OpenAI模型


def call_ollama(messages, model=OLLAMA_MODEL_NAME, temperature=0.7, system_prompt=None, max_tokens=None):
    """
    调用 Ollama API 进行对话

    参数:
        messages (list): 对话消息列表
        model (str): 使用的模型名称
        temperature (float): 温度参数，控制随机性
        system_prompt (str): 系统提示信息
        max_tokens (int): 生成的最大token数

    返回:
        str: 模型的回复内容
    """
    try:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }

        # 如果有系统提示，添加到消息列表开头
        if system_prompt:
            payload["messages"] = [{"role": "system", "content": system_prompt}] + messages

        # 如果指定了最大token数
        if max_tokens:
            payload["max_tokens"] = max_tokens

        response = requests.post(OLLAMA_API_ENDPOINT, json=payload)
        response.raise_for_status()  # 检查请求是否成功

        result = response.json()
        return result["message"]["content"]

    except Exception as e:
        print(f"调用 Ollama API 时出错: {str(e)}")
        return f"Error: {str(e)}"


def call_openai(messages, model=OPENAI_MODEL_NAME, temperature=0.7, system_prompt=None, max_tokens=None):
    """
    使用OpenAI Python包调用API进行对话

    参数:
        messages (list): 对话消息列表
        model (str): 使用的模型名称
        temperature (float): 温度参数，控制随机性
        system_prompt (str): 系统提示信息
        max_tokens (int): 生成的最大token数

    返回:
        str: 模型的回复内容
    """
    try:
        # 确保API密钥已设置
        if not openai.api_key:
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            if not openai.api_key:
                raise ValueError("OpenAI API密钥未设置，请设置OPENAI_API_KEY环境变量或直接设置openai.api_key")

        # 准备消息列表
        formatted_messages = messages.copy()

        # 如果有系统提示，添加到消息列表开头
        if system_prompt:
            formatted_messages = [{"role": "system", "content": system_prompt}] + formatted_messages

        # 准备API调用参数
        params = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature
        }

        # 如果指定了最大token数
        if max_tokens:
            params["max_tokens"] = max_tokens

        # 调用OpenAI API
        response = openai.ChatCompletion.create(**params)

        # 返回生成的文本
        return response.choices[0].message.content

    except Exception as e:
        print(f"调用 OpenAI API 时出错: {str(e)}")
        return f"Error: {str(e)}"


def load_conversation(file_path):
    """
    从JSON文件加载对话历史

    参数:
        file_path (str): JSON文件路径

    返回:
        list: 对话消息列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载对话文件时出错: {str(e)}")
        return []


def save_conversation_result(original_messages, responses, output_file):
    """
    保存对话结果到JSON文件

    参数:
        original_messages (list): 原始对话消息
        responses (list): 模型的回复列表
        output_file (str): 输出文件路径
    """
    # 创建完整对话列表，交替包含用户消息和助手回复
    full_conversation = []
    for i, msg in enumerate(original_messages):
        full_conversation.append(msg)  # 添加用户消息
        if i < len(responses):
            full_conversation.append({
                "role": "assistant",
                "content": responses[i]
            })  # 添加助手回复

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_conversation, f, ensure_ascii=False, indent=2)

    print(f"对话结果已保存到: {output_file}")


def main():
    # 配置文件路径
    input_file = "client/experiment/haystack/101.json"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 选择使用的API
    use_openai = True  # 设置为False使用Ollama
    api_type = "openai" if use_openai else "ollama"
    output_file = f"client/experiment/result/{api_type}_conversation_result_{timestamp}.json"

    # 模型设置
    model = OPENAI_MODEL_NAME if use_openai else OLLAMA_MODEL_NAME
    temperature = 0.7  # 可调整的温度参数
    system_prompt = "你是一个有帮助的AI助手。"  # 可自定义的系统提示
    max_tokens = 1000  # 可设置的最大生成token数

    # 加载对话历史
    conversation = load_conversation(input_file)
    if not conversation:
        print("无法加载对话历史，程序退出。")
        return

    print(f"已加载 {len(conversation)} 条对话消息")

    # 创建消息列表
    formatted_messages = []
    for msg in conversation:
        # 确保消息格式正确
        if "role" in msg and "content" in msg:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # 存储模型回复
    responses = []

    # 逐条处理用户消息，获取模型回复
    for i, msg in enumerate(formatted_messages):
        print(f"\n处理消息 {i + 1}/{len(formatted_messages)}:")
        print(f"用户: {msg['content'][:50]}..." if len(msg['content']) > 50 else f"用户: {msg['content']}")

        # 准备当前对话上下文 (只包含当前消息)
        current_context = [msg]

        # 调用 API
        if use_openai:
            response = call_openai(
                current_context,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )
        else:
            response = call_ollama(
                current_context,
                model=model,
                temperature=temperature,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )

        responses.append(response)

        print(f"助手: {response[:50]}..." if len(response) > 50 else f"助手: {response}")

    # 保存对话结果
    save_conversation_result(conversation, responses, output_file)


if __name__ == "__main__":
    main()