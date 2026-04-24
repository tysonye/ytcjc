import requests
import re

js_url = "https://jc.titan007.com/js/football.js"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
})

try:
    response = session.get(js_url, timeout=10)
    js_content = response.text
    
    print(f"JS 文件长度：{len(js_content)}")
    print(f"\n前 2000 字符:")
    print(js_content[:2000])
    
    print("\n\n查找 API 接口或数据 URL...")
    url_patterns = [
        r'url\s*[:=]\s*["\']([^"\']+)',
        r'ajax\s*\(\s*\{[^}]*url\s*[:=]\s*["\']([^"\']+)',
        r'["\'](https?://[^"\']*api[^"\']*)["\']',
    ]
    
    for pattern in url_patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        if matches:
            print(f"\n模式 {pattern[:40]}... 找到 {len(matches)} 个:")
            for m in matches[:5]:
                print(f"  - {m}")
    
    print("\n\n查找函数定义...")
    func_defs = re.findall(r'function\s+(\w+)', js_content)
    if func_defs:
        print(f"找到 {len(func_defs)} 个函数:")
        for func in func_defs[:20]:
            print(f"  - {func}")
            
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
