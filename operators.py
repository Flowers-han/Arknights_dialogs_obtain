import re
import requests
import os

def fetch_page(title: str) -> str:
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvslots": "main",
        "rvprop": "content",
        "format": "json",
        "titles": title
    }
    r = requests.get(url, params=params).json()
    page = next(iter(r["query"]["pages"].values()))
    return page["revisions"][0]["slots"]["main"]["*"]

def extract_voice_data(text: str) -> dict:
    """从语音记录页面提取语音数据"""
    voice_data = {}

    # 提取语音key和路径信息
    voice_key_match = re.search(r'\|\u8bed\u97f3key=([^\n]+)', text)
    if voice_key_match:
        voice_data['voice_key'] = voice_key_match.group(1).strip()

    path_match = re.search(r'\|\u8def\u5f84=([^\n]+)', text)
    if path_match:
        voice_data['voice_path'] = path_match.group(1).strip()

    # 提取所有语音条目
    voice_entries = []
    entry_pattern = r'\|\u6807\u9898(\d+)=([^\n]+)\n\|\u53f0\u8bcd\1=([^\n]+)\n\|\u8bed\u97f3\1=([^\n]+)(?:\n\|\u89e6\u53d1\u7c7b\u578b\1=([^\n]+))?(?:\n\|\u6761\u4ef6\1=([^\n]+))?'

    matches = re.finditer(entry_pattern, text)
    for match in matches:
        entry = {
            'id': match.group(1),
            'title': match.group(2).strip(),
            'dialogue': match.group(3).strip(),
            'voice_file': match.group(4).strip(),
            'trigger_type': match.group(5).strip() if match.group(5) else '',
            'condition': match.group(6).strip() if match.group(6) else ''
        }
        voice_entries.append(entry)

    voice_data['entries'] = voice_entries
    return voice_data

def extract_sections(text: str, sections=("干员信息","获得方式","天赋","模组", "相关道具", "干员档案")): # 需要的干员信息
    results = {}
    for sec in sections:
        # 允许模组下面包含三级标题，不要在 === 时截断
        pattern = rf"=={sec}==[\s\S]*?(?=\n==[^=]|\Z)"
        match = re.search(pattern, text)
        if match:
            results[sec] = match.group(0).strip()
    return results


def get_existing_operators():
    """获取已下载的干员列表"""
    ops_dir = "ops"
    if not os.path.exists(ops_dir):
        return []

    existing_operators = []
    for filename in os.listdir(ops_dir):
        if filename.endswith('.md'):
            # 移除.md后缀得到干员名
            operator_name = filename[:-4]
            existing_operators.append(operator_name)

    return existing_operators


def process_operator(op, force_update=False):
    """处理单个干员，force_update=True时强制更新"""
    filename = os.path.join("ops", f"{op}.md")

    # 如果文件已存在且不是强制更新，则跳过
    if os.path.exists(filename) and not force_update:
        return False, "已存在"

    try:
        print(f"正在处理 {op} ...")

        # 获取干员基本信息
        text = fetch_page(op)
        sections = extract_sections(text)

        # 获取语音记录
        voice_data = None
        try:
            voice_text = fetch_page(f"{op}/语音记录")
            voice_data = extract_voice_data(voice_text)
            print(f"  获取到 {len(voice_data.get('entries', []))} 条语音记录")
        except Exception as e:
            print(f"  获取语音记录失败: {str(e)}")

        # 保存为 md
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {op}\n\n")

            # 写入基本信息部分
            for sec, content in sections.items():
                f.write(f"## {sec}\n\n{content}\n\n")

            # 写入语音记录部分
            if voice_data and voice_data.get('entries'):
                f.write("## 语音记录\n\n")

                # 写入语音条目
                for entry in voice_data['entries']:
                    # 解析多语言对话内容，只提取中文
                    dialogue = entry['dialogue']
                    # 提取VoiceData/word模板中的内容
                    voice_matches = re.findall(r'\{\{VoiceData/word\|([^\|]+)\|([^}]+)\}\}', dialogue)

                    chinese_text = ""
                    if voice_matches:
                        # 只找中文内容
                        for lang, text in voice_matches:
                            if lang == '中文':
                                chinese_text = text
                                break
                    else:
                        # 如果没有VoiceData模板，使用原始内容
                        chinese_text = dialogue

                    # 将标题和对话内容合并到同一行，用冒号分隔
                    if chinese_text:
                        f.write(f"{entry['title']}: {chinese_text}\n\n")

        return True, f"已保存 {filename}"
    except Exception as e:
        return False, f"处理 {op} 失败: {str(e)}"


if __name__ == "__main__":
    # 读取干员列表
    with open("干员列表.txt", "r", encoding="utf-8") as f:
        all_operators = [line.strip() for line in f if line.strip()]

    # 确保存放目录存在
    os.makedirs("ops", exist_ok=True)

    # 获取已下载的干员
    existing_operators = set(get_existing_operators())
    print(f"已存在 {len(existing_operators)} 个干员文件")

    # 找出需要下载的干员（缺失的）
    missing_operators = [op for op in all_operators if op not in existing_operators]

    if not missing_operators:
        print("所有干员资料都已下载完成！")
    else:
        print(f"需要补充下载 {len(missing_operators)} 名干员资料")

        # 下载缺失的干员资料
        success_count = 0
        fail_count = 0
        failed_operators = []

        for i, op in enumerate(missing_operators, 1):
            success, message = process_operator(op)
            # 使用ASCII字符避免编码问题
            if success:
                status = "[OK]"
            else:
                status = "[ERROR]"
            print(f"[{i}/{len(missing_operators)}] {status} {op}: {message}")

            if success:
                success_count += 1
            else:
                fail_count += 1
                failed_operators.append(op)

        # 显示统计信息
        print(f"\n下载完成统计:")
        print(f"成功: {success_count} 名")
        print(f"失败: {fail_count} 名")

        if failed_operators:
            print(f"\n下载失败的干员:")
            for op in failed_operators:
                print(f"  - {op}")

        print(f"\n总计: {len(existing_operators) + success_count}/{len(all_operators)} 名干员已下载")
