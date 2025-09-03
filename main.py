from ark_dialog import fetch_wiki_text
from ark_dialog import save_dialogs_to_file
# 定义你想要获取的页面标题
with open("剧情章节标题.txt", "r", encoding="utf-8") as f:
    titles = [line.strip() for line in f if line.strip()]
for title in titles:
    # 获取并处理维基文本    
    dialogs = fetch_wiki_text(title)
    # 保存json到本地文件
    save_dialogs_to_file(dialogs, title)
