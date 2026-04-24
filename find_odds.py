
from bs4 import BeautifulSoup

# 读取保存的HTML文件
with open('page_content.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 80)
print("查找包含胜平负赔率的部分 (如 2.16 3.3 2.75 这种格式):")
print("=" * 80)

# 查找所有包含数字的文本，并且有连续小数的
import re

# 查找所有文本节点
all_text = list(soup.stripped_strings)

# 查找包含多个小数的文本
for i, text in enumerate(all_text):
    # 查找类似 "2.16 3.3 2.75" 这样的模式
    if '.' in text and ' ' in text:
        # 检查是否有多个小数
        parts = text.split()
        decimal_count = sum(1 for p in parts if '.' in p and p.replace('.', '', 1).isdigit())
        if decimal_count >= 3:
            print(f"\n--- 位置 {i} ---")
            print(f"文本: {text}")
            
            # 打印前后一些文本作为上下文
            context_start = max(0, i-5)
            context_end = min(len(all_text), i+10)
            for j in range(context_start, context_end):
                print(f"  {j}: {all_text[j]}")


print("\n" + "=" * 80)
print("查找div元素:")
print("=" * 80)

# 查找所有div并检查它们的内容
divs = soup.find_all('div')
for i, div in enumerate(divs):
    text = div.get_text(strip=True)
    if len(text) > 100 and any(key in text for key in ['胜', '平', '负', '球', '盘']):
        print(f"\n--- Div {i} ---")
        print(f"长度: {len(text)}")
        # 检查是否有小数
        if '.' in text:
            print(f"包含小数，可能是赔率")
            print(f"预览: {text[:300]}")
