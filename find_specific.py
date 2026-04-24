
# 读取全部文本
from bs4 import BeautifulSoup
with open('page_content.html', 'r', encoding='utf-8') as f:
    html = f.read()
soup = BeautifulSoup(html, 'html.parser')
all_text = list(soup.stripped_strings)

# 查找"胜平负/亚让
with open('find_specific_content.txt', 'w', encoding='utf-8') as f:
    for i, text in enumerate(all_text):
        if '胜平' in text or '亚让' in text or '胜平负' in text or '进球' in text:
            f.write(f"{i}: {text}\n")
            # 输出前后一些文本
            for j in range(max(0, i-3), min(len(all_text), i+20)):
                f.write(f"  {j}: {all_text[j]}\n")
            f.write("-"*80 + "\n")

print("已保存")
