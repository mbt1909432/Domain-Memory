import requests
import json
from datetime import datetime

# API 端点
API_URL = "http://localhost:8000/process_profile_from_chat"  # 根据实际部署情况修改

id=40
json_path=f'haystack/haystack_with_needle_at_{str(id)}.json'
output_path=f'result/haystack_with_needle_at_{str(id)}_result.json'

# Load the haystack from the JSON file
with open(json_path, 'r', encoding='utf-8') as f:
    haystack_with_needle = json.load(f)

# 发送请求
def process_profile_from_chat(chat):
    try:
        response = requests.post(API_URL, json=chat)

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
                return response.json()
            else:
                print(f"请求失败: {result.get('msg')}")
        else:
            print(f"请求失败: {response.text}")
    except Exception as e:
        print(f"测试异常: {str(e)}")


#process one by one
test_chat_from_1_to_10 = {
    "messages": haystack_with_needle[:10]  # First 10 messages
}
process_profile_from_chat(test_chat_from_1_to_10)

test_chat_from_11_to_20 = {
    "messages": haystack_with_needle[10:20]  # Messages 11 to 20
}
process_profile_from_chat(test_chat_from_11_to_20)

test_chat_from_21_to_30 = {
    "messages": haystack_with_needle[20:30]  # Messages 21 to 30
}
process_profile_from_chat(test_chat_from_21_to_30)

test_chat_from_30_to_40 = {
    "messages": haystack_with_needle[30:40]  # Messages 31 to 40
}
final_result=process_profile_from_chat(test_chat_from_30_to_40)


with open(output_path, 'w') as json_file:  # 以写入模式打开文件
    json.dump(final_result, json_file)  # 将final_result写入json文件


