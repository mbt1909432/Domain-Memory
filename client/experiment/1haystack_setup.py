import json
from datetime import datetime

# 获取当前日期并格式化
date_str = datetime.now().strftime("[%Y/%m/%d]")

# 从 raw.json 读取对话数据
with open('../raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
    # 提取前39条对话内容作为 haystack
    raw_haystack = [f"{date_str} {item['对话']}" for item in raw_data[:39]]

# Create four identical needle entries
needles = f"{date_str} 我练习篮球时长两年半了"


positions = [10, 20, 30, 40]


haystack_with_needle_at_10 = [
    {"role": "user", "content": item} for item in (raw_haystack[:9] + [needles] + raw_haystack[9:])
]
haystack_with_needle_at_20 = [
    {"role": "user", "content": item} for item in (raw_haystack[:19] + [needles] + raw_haystack[19:])
]
haystack_with_needle_at_30 = [
    {"role": "user", "content": item} for item in (raw_haystack[:29] + [needles] + raw_haystack[29:])
]
haystack_with_needle_at_40 = [
    {"role": "user", "content": item} for item in (raw_haystack[:39] + [needles] + raw_haystack[39:])
]

# Save each haystack with needle to a JSON file
with open('haystack/haystack_with_needle_at_10.json', 'w', encoding='utf-8') as f:
    json.dump(haystack_with_needle_at_10, f, ensure_ascii=False, indent=4)

with open('haystack/haystack_with_needle_at_20.json', 'w', encoding='utf-8') as f:
    json.dump(haystack_with_needle_at_20, f, ensure_ascii=False, indent=4)

with open('haystack/haystack_with_needle_at_30.json', 'w', encoding='utf-8') as f:
    json.dump(haystack_with_needle_at_30, f, ensure_ascii=False, indent=4)

with open('haystack/haystack_with_needle_at_40.json', 'w', encoding='utf-8') as f:
    json.dump(haystack_with_needle_at_40, f, ensure_ascii=False, indent=4)


