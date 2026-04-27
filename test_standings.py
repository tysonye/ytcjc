import requests
import re
import json
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'https://zq.titan007.com/',
})

url = "https://zq.titan007.com/analysis/2784814.htm"
resp = session.get(url, timeout=10)
html = resp.content.decode('GB18030', errors='replace')
soup = BeautifulSoup(html, 'html.parser')

print("=== Method 1: porlet_5 div ===")
porlet_5 = soup.find('div', id='porlet_5')
if porlet_5:
    outer_table = porlet_5.find('table')
    if outer_table:
        print(f"Found outer table")
        rows = outer_table.find_all('tr')
        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            print(f"Row {i}: {len(cells)} cells")
            for j, cell in enumerate(cells[:3]):
                txt = cell.get_text(strip=True)
                print(f"  Cell {j}: {txt[:50]}")
    print(f"\nporlet_5 text preview: {porlet_5.get_text(strip=True)[:300]}")
else:
    print("porlet_5 not found")

print("\n=== Method 2: JS variables ===")
for var_name in ['totalScoreStr', 'homeScoreStr', 'guestScoreStr']:
    m = re.search(rf'var\s+{var_name}\s*=\s*(\[.+?\]);', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            print(f"{var_name}: {len(data)} items")
            for item in data[:3]:
                print(f"  {item}")
        except:
            print(f"{var_name}: parse error: {m.group(1)[:200]}")
    else:
        print(f"{var_name}: NOT FOUND")

print("\n=== Method 3: League ID / sclass ===")
for pattern, label in [(r'sclass_ID\s*=\s*(\d+)', 'sclass_ID'), (r'sclass_Name\s*=\s*["\x27]([^"\x27]+)', 'sclass_Name')]:
    m = re.search(pattern, html)
    if m:
        print(f"{label}: {m.group(1)}")

print("\n=== Method 4: Find standings-related tables by headers ===")
tables = soup.find_all('table')
for i, t in enumerate(tables):
    txt = t.get_text(strip=True)[:50]
    rows = t.find_all('tr')
    if len(rows) >= 5:
        first_row = rows[0].get_text(strip=True)
        if '名次' in first_row or '积分' in first_row or '球队' in first_row:
            print(f"\nTable {i}: headers={first_row[:80]}")
            for r_idx, row in enumerate(rows[:8]):
                cells = row.find_all(['td', 'th'])
                cell_vals = [c.get_text(strip=True)[:15] for c in cells[:6]]
                print(f"  Row {r_idx}: {cell_vals}")

print("\n=== Method 5: Check for league standings API ===")
# The league standings URL pattern is usually:
# https://zq.titan007.com/cn/SoccerLeague/Schedule.aspx?sClassID={id}
# or similar
m = re.search(r'sclass_ID\s*=\s*(\d+)', html)
if m:
    sclass_id = m.group(1)
    print(f"League ID: {sclass_id}")
    # Try to find standings page links
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'standing' in href.lower() or 'jifen' in href.lower() or 'Schedule' in href:
            print(f"  Link: {link.get_text(strip=True)[:20]} -> {href[:100]}")
