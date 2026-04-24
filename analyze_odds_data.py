
from bs4 import BeautifulSoup

# 读取保存的HTML文件
with open('page_content.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# 保存所有文本到文件
all_text = list(soup.stripped_strings)

# 写入文件
with open('extracted_text.txt', 'w', encoding='utf-8') as f:
    for i, text in enumerate(all_text[:200]):
        f.write(f"{i}: {text}\n")

print(f"已保存前200条文本到 extracted_text.txt")

# 查找特定模式
import re

# 查找胜平负、亚盘等数据
with open('extracted_odds.txt', 'w', encoding='utf-8') as f:
    # 查找包含数字和胜平负的文本
    for i, text in enumerate(all_text):
        if any(key in text for key in ['胜', '平', '负', '亚', '胜平', '盘']):
            if len(text) > 10:
                f.write(f"{i}: {text}\n")
                
print(f"已保存包含关键词的文本到 extracted_odds.txt")
