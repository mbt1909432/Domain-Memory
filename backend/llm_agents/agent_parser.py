import re

# 示例字符串
text = """

-::人工智能在医疗领域的应用正在迅速扩展，涵盖了疾病诊断、药物研发和患者护理等多个方面。通过机器学习和大数据分析，
AI能够快速处理大量医疗数据，提供更精准的诊断
结果。此外，AI还在个性化治疗和远程医疗中发挥了重要作用，显著提高了医疗效率和患者体验。未来，随着技术的进一步发展，AI有望在医疗领域实现更多突破。::-
"""

def parser(data: str) -> str | None:
    pattern = r"-::(.*?)::-"
    match = re.search(pattern, data, re.DOTALL)  # 添加re.DOTALL标志

    if match:
        extracted_text = match.group(1)
        # print("Extracted content:", extracted_text)
        return extracted_text
    else:
        # print("No match found.")
        return None


if __name__=="__main__":
    print(parser(text))
