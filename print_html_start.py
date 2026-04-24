
# 读取HTML文件
with open('page_content.html', 'r', encoding='utf-8') as f:
    # 只读取前20000个字符
    content = f.read(20000)
    
print("=" * 80)
print("HTML文件前20000字符:")
print("=" * 80)
print(content)
