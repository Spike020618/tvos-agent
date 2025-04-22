
'''from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def bilibili_login():
    driver = webdriver.Chrome()
    driver.get("https://passport.bilibili.com/login")
    
    # 等待并输入账号密码
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username"))
    driver.find_element(By.ID, "login-username").send_keys("你的账号")
    driver.find_element(By.ID, "login-passwd").send_keys("你的密码")
    
    # 点击登录按钮
    driver.find_element(By.CLASS_NAME, "btn-login").click()
    
    # 等待登录完成（可能需要手动处理验证码）
    time.sleep(10)  # 留出时间处理验证码
    
    # 获取Cookies
    cookies = driver.get_cookies()
    print("获取的Cookies:", cookies)
    
    driver.quit()
    return cookies

if __name__ == "__main__":
    bilibili_login()'''