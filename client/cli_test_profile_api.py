import requests
import json
import argparse
from datetime import datetime


def create_message(role, content):
    """创建消息对象"""
    return {
        "role": role,
        "content": content,
        "created_at": datetime.now().isoformat()
    }


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="测试个人资料处理 API")
    parser.add_argument("--url", default="http://localhost:8000/process_profile_from_chat",
                        help="API 端点 URL")
    parser.add_argument("--model", default="gpt-4",
                        help="要使用的模型 ID")
    parser.add_argument("--messages", nargs="+", default=[],
                        help="聊天消息，格式为 'role:content'，例如 'user:我叫张三'")
    parser.add_argument("--file", help="包含预定义消息的 JSON 文件路径")
    
    return parser.parse_args()


def test_api(url, model, messages_data):
    """测试 API"""
    headers = {
        "Content-Type": "application/json",
        "Model": model
    }
    
    try:
        response = requests.post(url, json=messages_data, headers=headers)
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\n响应数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get("code") == 1:
                data = result.get("data", {})
                print("\n提取的个人资料信息:")
                for profile in data.get("extracted_profiles", {}).get("facts", []):
                    print(f"- {profile['domain']}/{profile['attribute']}: {profile['description']}")
                
                print("\n更新的个人资料信息:")
                for update in data.get("updates", []):
                    print(f"- {update['domain']}/{update['attribute']} ({update['action']}): {update['description']}")
                
                print("\n资料总结:")
                print(data.get("profile_summary", "无总结"))
            else:
                print(f"请求失败: {result.get('msg')}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"测试异常: {str(e)}")


def main():
    args = parse_args()
    
    # 检查是否提供了消息或文件
    if not args.messages and not args.file:
        # 使用默认测试消息
        messages = [
            create_message("user", "你好，我叫张三，今年28岁，来自北京，是一名软件工程师。"),
            create_message("assistant", "你好张三！很高兴认识你。你在软件工程领域有什么特别感兴趣的方向吗？"),
            create_message("user", "我主要做后端开发，使用Python和Go语言。我也喜欢旅游，上个月刚去了云南。"),
            create_message("assistant", "Python和Go是很棒的语言选择！云南是个美丽的地方，有什么特别喜欢的景点吗？"),
            create_message("user", "我最喜欢大理和丽江，那里的风景很美。我的电话是13812345678，如果有什么技术交流可以联系我。")
        ]
        messages_data = {"messages": messages}
    elif args.file:
        # 从文件加载消息
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
        except Exception as e:
            print(f"读取文件错误: {str(e)}")
            return
    else:
        # 从命令行参数构建消息
        messages = []
        current_role = "user"  # 默认角色
        
        for msg in args.messages:
            if ":" in msg:
                parts = msg.split(":", 1)
                role = parts[0].strip()
                content = parts[1].strip()
                if role not in ["user", "assistant"]:
                    print(f"警告: 角色 '{role}' 无效，使用 '{current_role}'")
                    role = current_role
                messages.append(create_message(role, content))
                # 交替角色
                current_role = "assistant" if role == "user" else "user"
            else:
                messages.append(create_message(current_role, msg))
                # 交替角色
                current_role = "assistant" if current_role == "user" else "user"
        
        messages_data = {"messages": messages}
    
    # 测试 API
    test_api(args.url, args.model, messages_data)


if __name__ == "__main__":
    #main()
    from datetime import datetime