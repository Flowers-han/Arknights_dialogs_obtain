import requests
from bs4 import BeautifulSoup

def fetch_titles():
    url = "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    titles = []
    for link in soup.find_all("a", href=True, title=True):
        title = link["title"]
        # 只要是剧情页（排除目录/锚点/文件等）
        if not title.startswith("File:") and not title.startswith("Special:"):
            titles.append(title)

    titles = sorted(set(titles))
    return titles


if __name__ == "__main__":
    titles = fetch_titles()
    with open("剧情章节标题.txt", "w", encoding="utf-8") as f:
        for t in titles:
            f.write(t + "\n")
    print(f"共获取 {len(titles)} 个标题，已保存到 剧情章节标题.txt")
