
from bs4 import BeautifulSoup

# 读取保存的HTML文件
with open('page_content.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# 查找所有div和table，找到包含数据的部分
print("=" * 80)
print("查找包含 '胜平负'、'亚让'、'进球' 关键词的元素:")
print("=" * 80)

# 查找所有文本包含这些关键词的元素
keywords = ['胜平负', '亚让', '进球', '胜', '平', '负', '亚盘', '初盘', '即时', '大小']

for keyword in keywords:
    elements = soup.find_all(text=lambda text: text and keyword in text)
    if elements:
        print(f"\n包含 '{keyword}' 的元素: {len(elements)} 个")
        
        # 查看每个元素的父级结构
        for i, elem in enumerate(elements[:3]):
            parent = elem.parent
            if parent:
                print(f"\n--- 元素 {i+1} ---")
                print(f"标签: {parent.name}")
                print(f"内容: {parent.get_text(strip=True)[:200]}")
                
                # 往上找几个父级
                grand = parent.parent
                if grand:
                    print(f"父标签: {grand.name}")
                    print(f"父内容: {grand.get_text(strip=True)[:300]}")


print("\n" + "=" * 80)
print("查找所有包含特定文本的表格 (更多样化):")
print("=" * 80)

tables = soup.find_all('table')
for i, table in enumerate(tables):
    text = table.get_text(strip=True)
    # 查找有实际数据内容的表格
    if len(text) > 50 and any(key in text for key in ['胜', '平', '负', '球', '赢', '输']):
        print(f"\n--- 表格 {i} ---")
        print(f"长度: {len(text)}")
        
        # 查看前几行
        rows = table.find_all('tr')
        print(f"行数: {len(rows)}")
        
        for j, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            cell_texts = [c.get_text(strip=True) for c in cells if c.get_text(strip=True)]
            if cell_texts:
                print(f"  行 {j+1}: {cell_texts}")
