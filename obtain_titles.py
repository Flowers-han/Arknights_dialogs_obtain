import requests

def get_story_titles():
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": "Category:剧情",
        "cmlimit": "max"
    }

    titles = []
    while True:
        r = requests.get(url, params=params).json()
        pages = r["query"]["categorymembers"]
        titles.extend([p["title"] for p in pages])

        # 翻页
        if "continue" in r:
            params.update(r["continue"])
        else:
            break

    return titles


if __name__ == "__main__":
    stories = get_story_titles()
    print(f"共获取 {len(stories)} 个剧情页面")
    for t in stories[:20]:  # 先看前20个
        print(t)
    with open("剧情标题.txt", "w", encoding="utf-8") as f:
        for t in stories:
            f.write(t + "\n")