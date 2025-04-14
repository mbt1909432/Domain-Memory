import requests
import json
from datetime import datetime

# API 端点
API_URL = "http://localhost:8000/process_profile_from_chat"  # 根据实际部署情况修改

# 构造测试数据
test_chat = {
    "messages": [
        {
            "role": "user",
            "content": "你好，我叫张三，今年28岁，来自北京，是一名软件工程师。",
        },
        {
            "role": "assistant",
            "content": "你好张三！很高兴认识你。你在软件工程领域有什么特别感兴趣的方向吗？",
        },
        {
            "role": "user",
            "content": "我主要做后端开发，使用Python和Go语言。我也喜欢旅游，上个月刚去了云南。",
        },
        {
            "role": "assistant",
            "content": "Python和Go是很棒的语言选择！云南是个美丽的地方，有什么特别喜欢的景点吗？",
        },
        {
            "role": "user",
            "content": "我最喜欢大理和丽江，那里的风景很美。我的电话是13812345678，如果有什么技术交流可以联系我。",
        }
    ]
}

# 请求头
headers = {
    "Content-Type": "application/json",
    "Model": "gpt-4"  # 可选的模型ID
}

# 发送请求
def test_process_profile_from_chat():
    try:
        response = requests.post(API_URL, json=test_chat, headers=headers)
        
        # 打印响应状态和内容
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("\n响应数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 检查响应中的关键字段
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

if __name__ == "__main__":
    test_process_profile_from_chat() 