
# 解析周五006的数据
line = "2799985^2026,3,25,00,30,00^2026,3,25,00,29,03^1^周五006^9^132^1344^杜塞尔多夫,杜斯多夫,杜塞多夫^425^德累斯顿,特雷斯登,德累斯顿^2^0^^^0^0^0^0^17^11^2026,3,24,00,00,00^0.25^0"

fields = line.split('^')
print(f"总字段数: {len(fields)}")
print("\n字段解析:")
for i, f in enumerate(fields):
    print(f"[{i:2}] {f}")

print("\n关键字段:")
print(f"[11] 主队半场比分: {fields[11]}")
print(f"[12] 客队半场比分: {fields[12]}")
print(f"[13] 主队全场比分: {fields[13]}")
print(f"[14] 客队全场比分: {fields[14]}")
print(f"[15] 红黄牌: {fields[15]}")
print(f"[16] 初盘主胜: {fields[16]}")
print(f"[17] 初盘平局: {fields[17]}")
print(f"[18] 初盘客胜: {fields[18]}")
print(f"[19] 即时主胜: {fields[19]}")
print(f"[20] 即时平局: {fields[20]}")
print(f"[21] 即时客胜: {fields[21]}")
print(f"[22] 让球盘口: {fields[22]}")
