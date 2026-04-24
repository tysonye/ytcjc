
import requests

url = "https://jc.titan007.com/xml/bf_jc.txt"

headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=10)
response.encoding = 'utf-8'

with open('data_raw.txt', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("数据已保存到 data_raw.txt")
print(f"长度: {len(response.text)}")

lines = response.text.split('\n')
print(f"行数: {len(lines)}")

print("\n前3行内容:")
for i, line in enumerate(lines[:5]):
    print(f"\n{i+1}. 长度:{len(line)}")
    if line:
        print(line[:200])
