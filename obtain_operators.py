import requests
import os

def get_operators():
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:干员",  # 分类名称
        "cmlimit": "max"
    }

    titles = []
    while True:
        r = requests.get(url, params=params).json()
        pages = r["query"]["categorymembers"]
        titles.extend([p["title"] for p in pages])

        # 处理翻页
        if "continue" in r:
            params.update(r["continue"])
        else:
            break

    return titles


def load_existing_operators():
    """从已有文件加载干员列表"""
    try:
        with open("干员列表.txt", "r", encoding="utf-8") as f:
            operators = [line.strip() for line in f.readlines() if line.strip()]
        return operators
    except FileNotFoundError:
        return []


def save_operators(operators):
    """保存干员列表到文件"""
    with open("干员列表.txt", "w", encoding="utf-8") as f:
        for op in operators:
            f.write(op + "\n")


if __name__ == "__main__":
    # 获取网站上的干员列表
    print("正在从网站获取干员列表...")
    website_operators = get_operators()
    print(f"网站共有 {len(website_operators)} 名干员")

    # 加载本地干员列表
    local_operators = load_existing_operators()
    print(f"本地文件有 {len(local_operators)} 名干员")

    if not local_operators:
        # 本地文件不存在，直接保存
        print("未找到本地干员列表文件，开始创建...")
        save_operators(website_operators)
        print(f"已保存 {len(website_operators)} 名干员到本地文件")
        print("\n前20个干员:")
        for op in website_operators[:20]:
            print(op)
    else:
        # 对比本地和网站的干员数量
        if len(website_operators) > len(local_operators):
            # 网站干员更多，需要更新
            update_count = len(website_operators) - len(local_operators)
            print(f"发现更新！网站比本地多 {update_count} 名干员")

            # 找出新增的干员
            local_set = set(local_operators)
            new_operators = [op for op in website_operators if op not in local_set]

            print(f"\n新增干员列表 ({len(new_operators)} 名):")
            for i, op in enumerate(new_operators, 1):
                print(f"{i}. {op}")

            # 更新本地文件
            save_operators(website_operators)
            print(f"\n已更新本地文件，现在共有 {len(website_operators)} 名干员")

        elif len(website_operators) < len(local_operators):
            # 这种情况不应该发生，但给出提示
            print(f"警告：网站干员数量 ({len(website_operators)}) 少于本地文件 ({len(local_operators)})")
            print("可能是网站数据异常或分类变更")
            print("本地文件保持不变")

        else:
            # 数量相同
            print("干员数量一致，无需更新")
            print("\n前20个干员:")
            for op in local_operators[:20]:
                print(op)