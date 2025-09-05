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

def extract_sections(text: str, sections=("干员信息","获得方式","天赋","模组", "相关道具", "干员档案", "语音记录")): # 需要的干员信息
    results = {}
    for sec in sections:
        # 允许模组下面包含三级标题，不要在 === 时截断
        pattern = rf"=={sec}==[\s\S]*?(?=\n==[^=]|\Z)"
        match = re.search(pattern, text)
        if match:
            results[sec] = match.group(0).strip()
    return results


if __name__ == "__main__":
    # 读取 operators.txt，每行一个干员名
    with open("干员列表.txt", "r", encoding="utf-8") as f:
        operators = [line.strip() for line in f if line.strip()]

    # 确保存放目录存在
    os.makedirs("ops", exist_ok=True)

    for op in operators:
        print(f"🔍 正在处理 {op} ...")
        text = fetch_page(op)
        sections = extract_sections(text)

        # 保存为 txt
        filename = os.path.join("ops", f"{op}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {op}\n\n")
            for sec, content in sections.items():
                f.write(f"## {sec}\n\n{content}\n\n")

        print(f"✅ 已保存 {filename}")
