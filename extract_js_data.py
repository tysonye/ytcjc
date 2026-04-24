
import requests
import re

url = "https://zq.titan007.com/analysis/2913592.htm"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers, timeout=15)
response.encoding = 'utf-8'

text = response.text

# 找到所有var声明
var_pattern = r'var\s+(\w+)\s*=\s*'
vars_found = re.findall(var_pattern, text)

print("找到的变量:")
for var in vars_found:
    print(f"  {var}")

# 提取具体数据
print("\n" + "="*80)

# 提取 Vs_eOdds
eodds_match = re.search(r'var\s+Vs_eOdds\s*=\s*(\[.*?\]);', text, re.DOTALL)
if eodds_match:
    print("\n欧洲指数数据找到!")
    data_str = eodds_match.group(1)[:500]
    print(data_str)

# 提取 Vs_hOdds
hodds_match = re.search(r'var\s+Vs_hOdds\s*=\s*(\[.*?\]);', text, re.DOTALL)
if hodds_match:
    print("\n亚洲盘口数据找到!")
    data_str = hodds_match.group(1)[:500]
    print(data_str)

# 提取 v_data (对赛往绩)
vdata_match = re.search(r'var\s+v_data\s*=\s*(\[.*?\]);', text, re.DOTALL)
if vdata_match:
    print("\n对赛往绩数据找到!")
    data_str = vdata_match.group(1)[:300]
    print(data_str)

# 提取 h_data (主队近期)
hdata_match = re.search(r'var\s+h_data\s*=\s*(\[.*?\]);', text, re.DOTALL)
if hdata_match:
    print("\n主队近期数据找到!")
    print(f"数据长度: {len(hdata_match.group(1))}")

# 提取 a_data (客队近期)
adata_match = re.search(r'var\s+a_data\s*=\s*(\[.*?\]);', text, re.DOTALL)
if adata_match:
    print("\n客队近期数据找到!")
    print(f"数据长度: {len(adata_match.group(1))}")
