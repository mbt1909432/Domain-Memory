# Profile API 测试工具

这个项目提供了用于测试个人资料处理 API（`/process_profile_from_chat`）的工具。

## 依赖项安装

在使用测试工具前，请先安装必要的依赖：

```bash
pip install requests pandas openpyxl
```

## Excel 转 JSON 工具

`excel_to_json.py` 是一个用于将 Excel 文件转换为 JSON 格式的工具。

使用方法：

```bash
# 基本用法（输出文件名将自动生成）
python excel_to_json.py input.xlsx

# 指定输出文件名
python excel_to_json.py input.xlsx -o output.json
```

### 功能特点

- 支持读取 Excel 文件（.xlsx, .xls）
- 自动生成带时间戳的输出文件名
- 支持自定义输出文件名
- 保持中文字符的正确编码
- 提供数据预览功能
- 显示处理数据的总行数

## 简单的测试脚本

`test_process_profile_api.py` 是一个简单的测试脚本，包含预定义的测试数据。

使用方法：

```bash
python test_process_profile_api.py
```

这个脚本会使用内置的测试消息发送请求到 API，并打印结果。

## 命令行测试工具

`cli_test_profile_api.py` 是一个更灵活的命令行工具，支持多种参数配置。

使用方法：

```bash
# 使用默认测试数据
python cli_test_profile_api.py

# 指定 API 端点和模型
python cli_test_profile_api.py --url http://example.com/api --model gpt-3.5-turbo

# 从命令行参数提供消息
python cli_test_profile_api.py --messages "user:我叫王五" "assistant:你好王五" "user:我今年25岁，是一名教师"

# 从文件加载消息
python cli_test_profile_api.py --file sample_chat.json
```

### 命令行参数说明

- `--url`: API 端点 URL，默认为 `http://localhost:8000/process_profile_from_chat`
- `--model`: 要使用的模型 ID，默认为 `gpt-4`
- `--messages`: 聊天消息列表，格式为 `role:content`，如 `user:我叫张三`
- `--file`: 包含预定义消息的 JSON 文件路径

## 示例 JSON 文件

`sample_chat.json` 是一个示例聊天数据文件，可用于从文件测试 API：

```bash
python cli_test_profile_api.py --file sample_chat.json
```

## API 响应格式

测试工具会解析 API 的响应并打印出关键信息：

1. 提取的个人资料信息
2. 更新的个人资料信息
3. 资料总结

如果 API 调用失败，则会显示错误信息。

## 更新记录

- 2023-09-16: 修复了 API 响应判断逻辑的问题，现在正确使用 `code == 1` 判断成功，而不是使用 `success` 字段
- 2023-09-16: 添加了 Excel 转 JSON 工具 `excel_to_json.py`