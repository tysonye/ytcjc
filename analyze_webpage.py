
import requests
from bs4 import BeautifulSoup
import re

# 获取网页内容
url = "https://zq.titan007.com/analysis/2913592.htm"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有script标签中的数据
scripts = soup.find_all('script')

for i, script in enumerate(scripts):
    if script.string and ('var ' in script.string or 'let ' in script.string):
        print(f"\n{'='*80}")
        print(f"Script {i}:")
        print(f"{'='*80}")
        
        # 查找变量定义
        text = script.string
        
        # 查找数组数据
        patterns = [
            r'var\s+(\w+)\s*=\s*(\[.*?\]);',
            r'let\s+(\w+)\s*=\s*(\[.*?\]);',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for var_name, data in matches[:5]:
                print(f"\n变量: {var_name}")
                # 只显示前200字符
                data_preview = data[:200].replace('\n', ' ')
                print(f"数据预览: {data_preview}...")
                print(f"数据长度: {len(data)}")
