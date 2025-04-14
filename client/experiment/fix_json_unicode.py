import json
import codecs

def fix_json_unicode(input_file, output_file=None):
    """
    修复 JSON 文件中的 Unicode 编码，转换为可读的中文字符
    
    参数:
        input_file (str): 输入 JSON 文件路径
        output_file (str, optional): 输出 JSON 文件路径，如果为 None，则覆盖输入文件
    
    返回:
        bool: 操作是否成功
    """
    if output_file is None:
        output_file = input_file
    
    try:
        # 读取 JSON 文件
        with codecs.open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 写入转换后的 JSON 文件（这一步会自动将 Unicode 转为中文字符）
        with codecs.open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"已成功修复 JSON 文件中的 Unicode 编码: {output_file}")
        return True
    
    except Exception as e:
        print(f"修复 JSON 文件时出错: {str(e)}")
        return False

if __name__ == '__main__':
    # 使用示例
    input_json = fr"E:\pycharm_project\ProLTM\client\experiment\result\haystack_with_needle_at_10_result.json"
    # 如果你想保留原文件，可以指定新的输出文件
    # output_json = "client/experiment/result/haystack_with_needle_at_40_result_fixed.json"
    
    fix_json_unicode(input_json) 