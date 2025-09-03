import re

def extract_dialog_json(raw_text: str):
    lines = raw_text.splitlines()
    dialogs = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过 {{模板}} 行
        if line.startswith("{{") and line.endswith("}}"):
            continue

        # 匹配对白行: [name="xxx"]  内容
        match = re.match(r'\[name="([^"]+)"\]\s*(.*)', line)
        if match:
            speaker, content = match.groups()
            if content:  # 有台词
                dialogs.append({"speaker": speaker, "text": content})
            continue

        # 如果是没有 name 的纯文本对白（叙述/旁白）
        if not line.startswith("[") and not line.startswith("}"):
            dialogs.append({"speaker": "旁白", "text": line})

    return dialogs

