
# 正确解析数据
with open('data_raw.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# 拆分联赛部分和比赛部分
parts = data.split('$')
print(f"总部分数: {len(parts)}")
print()

league_part = parts[0] if parts else ""
matches_part = parts[1] if len(parts) > 1 else ""

print("联赛部分长度:", len(league_part))
print("比赛部分长度:", len(matches_part))
print()

# 解析比赛
matches = matches_part.split('!')
print(f"找到 {len(matches)} 场比赛")
print()

for i, match_str in enumerate(matches[:5]):
    if not match_str:
        continue
    
    fields = match_str.split('^')
    print(f"{'='*100}")
    print(f"比赛 {i+1}, 字段数: {len(fields)}")
    print(f"{'='*100}")
    
    for j, f in enumerate(fields):
        if f:
            print(f"[{j:2}] {repr(f)}")
    print()
