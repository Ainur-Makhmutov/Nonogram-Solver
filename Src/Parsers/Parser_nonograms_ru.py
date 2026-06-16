from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()  # убедитесь, что chromedriver в PATH
driver.get('https://www.nonograms.ru/nonograms/i/81184')
time.sleep(3)  # ждём загрузки

# Ищем скрипты
scripts = driver.find_elements(By.TAG_NAME, 'script')
for script in scripts:
    content = script.get_attribute('innerHTML')
    if content and 'var d =' in content:
        print(content[:500])
        break


driver.quit()