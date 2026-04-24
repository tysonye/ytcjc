import re

raw_data = """场 赛事时间状态主队比分客队竞彩指数数据 AI 预测 2026 年 4 月 24 日 星期五（11:00 - 次日 11:00）收起 周五 001 澳超 17:35 麦克阿瑟 - 惠灵顿 2.163.752.50 亚欧析荐话题 (18) AI 预测 -14.30 4.201.52 周五 002 日职联 18:00 柏太阳神 - 鹿岛鹿角 2.363.252.52 亚欧析荐话题 (13) AI 预测 -15.50 3.951.44"""

print("原始数据前 200 字符:")
print(raw_data[:200])
print("\n")

clean_data = re.sub(r'\s+', ' ', raw_data)
print("清理后前 200 字符:")
print(clean_data[:200])
print("\n")

print("查找周五 001:")
if '周五 001' in clean_data:
    print("找到 周五 001")
    idx = clean_data.find('周五 001')
    print(f"位置：{idx}")
    print(f"上下文：{clean_data[idx:idx+100]}")
else:
    print("未找到")

print("\n\n查找数字:")
digits = re.findall(r'\d+\.\d{2}', clean_data)
print(f"找到 {len(digits)} 个赔率数字")
print(f"前 10 个：{digits[:10]}")

print("\n\n查找比赛编号模式:")
match_ids = re.findall(r'(周五 | 周六 | 周日)\d{3}', clean_data)
print(f"找到 {len(match_ids)} 个比赛编号")
print(f"前 5 个：{match_ids[:5]}")

print("\n\n使用简单模式查找:")
simple_pattern = r'周五 001.*?亚欧'
match = re.search(simple_pattern, clean_data)
if match:
    print(f"找到：{match.group()}")
else:
    print("未找到")
