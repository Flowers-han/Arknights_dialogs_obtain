import requests
import re
import os

from ark_dialog_process import extract_dialog_json

def fetch_wiki_text(title: str):
    url = "https://prts.wiki/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvslots": "main",
        "rvprop": "content",
        "format": "json",
        "titles": title
    }

    r = requests.get(url, params=params)
    data = r.json()
    page = next(iter(data["query"]["pages"].values()))
    text = page["revisions"][0]["slots"]["main"]["*"]
    produced_text = extract_dialog_json(text)  # ← 返回 list[dict]
    return produced_text

def save_dialogs_to_file(dialogs, title):
    os.makedirs("txts", exist_ok=True)
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    filename = os.path.join("txts", f"{safe_title}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        for d in dialogs:
            speaker = d.get("speaker", "旁白")
            text = d.get("text", "").strip()
            f.write(f"**{speaker}**：{text}\n\n")

    print(f"✅ 已保存对白 -> {filename}")
