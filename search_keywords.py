
import re

with open('page_content.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 查找包含"胜平"的位置
positions = []
for match in re.finditer('胜平|亚让|胜平负|进球数', html):
    positions.append(match.start())

# 打印每个位置附近的文本
with open('keyword_context.txt', 'w', encoding='utf-8') as f:
    for pos in positions[:20]:
        f.write("="*80 + "\n")
        f.write(f"Position: {pos}\n")
        f.write("="*80 + "\n")
        start = max(0, pos - 200)
        end = pos + 800
        f.write(html[start:end] + "\n")

print(f"已保存 {len(positions)} 个位置到 keyword_context.txt")
