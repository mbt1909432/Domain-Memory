from pydantic import BaseModel, Field
from typing import List
from schemas.agents.profile.profile_schema import UserProfiles,UserProfile

llm_tab_separator="::"

def format_profile_data(data):
    """
    将Pydantic模型或字典转换为格式化的个人资料字符串
    
    格式: - domain::attribute::description
    
    示例:
    ```
    - basic_info::Age::30岁（生日是2023/09/15）
    - work::profession::软件工程师
    ```
    
    Args:
        data: Pydantic模型(UserProfile, UserProfiles或包含facts列表的字典)
        
    Returns:
        str: 格式化的个人资料字符串
    """
    formatted_lines = []
    
    # 如果是单个UserProfile模型
    if isinstance(data, UserProfile):
        return f"- {data.domain}{llm_tab_separator}{data.attribute}{llm_tab_separator}{data.description}"
    
    # 如果是UserProfiles模型
    if isinstance(data, UserProfiles):
        for profile in data.facts:
            formatted_lines.append(
                f"- {profile.domain}{llm_tab_separator}{profile.attribute}{llm_tab_separator}{profile.description}"
            )
        return "\n".join(formatted_lines)
    
    # 如果是字典，首先检查是否有facts键
    if isinstance(data, dict) and 'facts' in data and isinstance(data['facts'], list):
        for item in data['facts']:
            if isinstance(item, dict) and all(k in item for k in ['domain', 'attribute', 'description']):
                formatted_lines.append(
                    f"- {item['domain']}{llm_tab_separator}{item['attribute']}{llm_tab_separator}{item['description']}"
                )
        if formatted_lines:
            return "\n".join(formatted_lines)
    
    # 如果是Pydantic模型，转换为字典
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):
        data = data.dict()
    
    # 处理一般字典结构
    def process_dict(d, prefix=""):
        for key, value in d.items():
            if isinstance(value, dict):
                # 处理嵌套字典
                process_dict(value, f"{prefix}{key}{llm_tab_separator}" if prefix else f"{key}")
            else:
                # 生成格式化行
                if prefix:
                    formatted_lines.append(f"- {prefix}{key}{llm_tab_separator}{value}")
                else:
                    # 没有前缀，意味着是顶级键
                    formatted_lines.append(f"- {key}{llm_tab_separator}{value}")
    
    process_dict(data)
    return "\n".join(formatted_lines)

def parse_profile_to_json(profile_text):
    """
    将格式化的个人资料字符串解析为嵌套字典
    
    Args:
        profile_text: 格式化的个人资料字符串，每行格式为 "- domain::attribute::description"
        
    Returns:
        dict: 解析后的嵌套字典
    """
    result = {}
    
    for line in profile_text.strip().split("\n"):
        line = line.strip()
        if not line or not line.startswith("-"):
            continue
            
        # 移除开头的 "- " 并按分隔符拆分
        parts = line[2:].split(llm_tab_separator, 2)
        if len(parts) < 3:
            continue
            
        domain, attribute, description = parts
        
        # 创建嵌套结构
        if domain not in result:
            result[domain] = {}
        
        result[domain][attribute] = description
    
    return result

def parse_profile_to_pydantic(profile_text):
    """
    将格式化的个人资料字符串解析为UserProfiles对象
    
    Args:
        profile_text: 格式化的个人资料字符串，每行格式为 "- domain::attribute::description"
        
    Returns:
        UserProfiles: 包含所有用户资料的Pydantic模型
    """
    facts = []
    
    for line in profile_text.strip().split("\n"):
        line = line.strip()
        if not line or not line.startswith("-"):
            continue
            
        # 移除开头的 "- " 并按分隔符拆分
        parts = line[2:].split(llm_tab_separator, 2)
        if len(parts) < 3:
            continue
            
        domain, attribute, description = parts
        
        # 创建UserProfile对象
        profile = UserProfile(
            domain=domain,
            attribute=attribute,
            description=description
        )
        facts.append(profile)
    
    return UserProfiles(facts=facts)



if __name__ == "__main__":
    # 示例用法
    test_profile_text = """
  Raw result:2131312
- basic_info::name::John Smith
- basic_info::age::32 years old
- work::profession::software engineer
- work::company::Google
- contact_info::city::San Francisco
- plan::relocation::moved to San Francisco about 5 years ago
- education::school::graduated from MIT
- education::major::computer science degree
sdfs
    """
    
    # 解析为嵌套字典
    profile_dict = parse_profile_to_json(test_profile_text)
    print("嵌套字典格式:")
    print(profile_dict)
    print()
    
    # 解析为Pydantic模型
    profile_model = parse_profile_to_pydantic(test_profile_text)
    print("Pydantic模型格式:")
    print(profile_model.model_dump())
    print()
    
    # 将Pydantic模型转换回格式化字符串
    formatted_text = format_profile_data(profile_model)
    print("重新格式化后:")
    print(formatted_text)
    
    # 新的示例：直接创建Pydantic模型并格式化
    print("\n直接创建Pydantic模型示例:")
    direct_model = UserProfiles(facts=[
        UserProfile(
            domain="basic_info",
            attribute="Age",
            description="30岁（生日是2023/09/15）"
        ),
        UserProfile(
            domain="work",
            attribute="profession",
            description="软件工程师"
        ),
        UserProfile(
            domain="contact_info",
            attribute="city",
            description="计划去杭州定居"
        )
    ])
    
    # 直接格式化
    direct_formatted = format_profile_data(direct_model)
    print(direct_formatted)
    
    # 示例：单个UserProfile的格式化
    data = UserProfile(
        domain="basic_info",
        attribute="Age",
        description="30岁（生日是2023/09/15）"
    )
    # 格式化单个UserProfile
    single_formatted = format_profile_data(data)
    print("\n单个UserProfile格式化示例:")
    print(single_formatted)  # 输出: - basic_info::Age::30岁（生日是2023/09/15）
