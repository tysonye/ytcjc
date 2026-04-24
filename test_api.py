import re

test = "周五 001"
print(f"测试字符串：'{test}'")
print(f"字节：{test.encode('utf-8')}")

patterns = [
    r'周 [五六日]\d{3}',
    r'周五 \d{3}',
    r'周.{1}\d{3}',
    r'周.+\d{3}',
    r'.*\d{3}',
]

for pattern in patterns:
    match = re.match(pattern, test)
    print(f"模式 '{pattern}': {match}")
