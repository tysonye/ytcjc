
# 直接读取HTML文件，打印一些内容
with open('page_content.html', 'r', encoding='utf-8') as f:
    # 读取前30000个字符
    html = f.read(30000)
    
with open('html_sample.txt', 'w', encoding='utf-8') as f:
    f.write(html)

print("已保存到 html_sample.txt")
