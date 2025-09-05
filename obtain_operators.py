import requests

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


if __name__ == "__main__":
    ops = get_operators()
    print(f"共获取 {len(ops)} 名干员")
    for op in ops[:20]:  # 只看前20个
        print(op)
    with open("干员列表.txt", "w", encoding="utf-8") as f:
        for op in ops:
            f.write(op + "\n")