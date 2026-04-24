
import subprocess
import json

# 使用curl或wget获取网页
try:
    # 尝试使用requests with session
    import requests
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    
    # 首先访问主页获取cookie
    main_url = "https://jc.titan007.com/index.aspx"
    response = session.get(main_url, timeout=15)
    print(f"主页状态: {response.status_code}")
    print(f"Cookie: {session.cookies.get_dict()}")
    
    # 尝试获取实时数据
    # 通常这种网站会有定时刷新的接口
    live_url = "https://jc.titan007.com/xml/bf_jc.txt"
    response2 = session.get(live_url, timeout=10)
    print(f"\n数据接口状态: {response2.status_code}")
    
    if response2.status_code == 200:
        # 查找时间数据
        if '2799985' in response2.text:
            idx = response2.text.find('2799985')
            context = response2.text[idx:idx+300]
            print(f"\n找到比赛2799985的数据:")
            print(context)
            
except Exception as e:
    print(f"错误: {e}")
