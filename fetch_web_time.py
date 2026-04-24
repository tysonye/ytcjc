
import requests
from bs4 import BeautifulSoup

# 获取网页数据
url = "https://jc.titan007.com/index.aspx"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有时间元素
time_elements = soup.find_all('i', class_='t')
print(f"找到 {len(time_elements)} 个时间元素")

for elem in time_elements[:10]:
    print(f"  时间: {elem.text}, class: {elem.get('class')}")

# 也查找td中的时间
td_times = soup.find_all('td', id=lambda x: x and x.startswith('time_'))
print(f"\n找到 {len(td_times)} 个td时间元素")

for td in td_times[:5]:
    match_id = td.get('id', '').replace('time_', '')
    time_elem = td.find('i')
    if time_elem:
        print(f"  比赛ID: {match_id}, 时间: {time_elem.text}, class: {time_elem.get('class')}")
