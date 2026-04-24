
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 启动浏览器
driver = webdriver.Chrome()

try:
    # 打开网页
    driver.get("https://jc.titan007.com/index.aspx")
    
    # 等待页面加载
    time.sleep(5)
    
    # 查找所有时间元素
    time_elements = driver.find_elements(By.CSS_SELECTOR, 'td[id^="time_"]')
    
    print(f"找到 {len(time_elements)} 个时间元素")
    
    for elem in time_elements[:10]:
        match_id = elem.get_attribute('id').replace('time_', '')
        try:
            time_text = elem.find_element(By.TAG_NAME, 'i').text
            time_class = elem.find_element(By.TAG_NAME, 'i').get_attribute('class')
            print(f"  比赛ID: {match_id}, 时间: {time_text}, class: {time_class}")
        except:
            print(f"  比赛ID: {match_id}, 无时间数据")

finally:
    driver.quit()
