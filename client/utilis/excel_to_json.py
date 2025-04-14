import pandas as pd
import json
from datetime import datetime
import argparse


def excel_to_json(excel_file, output_file=None):
    """
    将 Excel 文件转换为 JSON 格式

    Args:
        excel_file: Excel 文件路径
        output_file: 输出 JSON 文件路径，如果不指定则使用默认名称
    """
    try:
        # 读取 Excel 文件
        df = pd.read_excel(excel_file)

        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 如果没有指定输出文件，则使用默认名称
        if output_file is None:
            output_file = f"output_{timestamp}.json"

        # 将 DataFrame 转换为 JSON 格式
        # orient='records' 表示每行数据作为一个独立的 JSON 对象
        json_data = df.to_json(orient='records', force_ascii=False, indent=2)

        # 将 JSON 字符串写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)

        print(f"转换完成！输出文件：{output_file}")
        print(f"共处理 {len(df)} 行数据")

        # 打印前几行数据作为预览
        print("\n数据预览（前3行）：")
        print(json.dumps(json.loads(json_data)[:3], ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"转换过程中出错：{str(e)}")


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="将 Excel 文件转换为 JSON 格式")
    parser.add_argument("excel_file", help="输入的 Excel 文件路径")
    parser.add_argument("--output", "-o", help="输出的 JSON 文件路径（可选）")

    # 解析命令行参数
    args = parser.parse_args()

    # 执行转换
    excel_to_json(args.excel_file, args.output)


if __name__ == "__main__":
    main()