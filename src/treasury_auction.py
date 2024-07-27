import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random


with open("../metadata/Chrome.txt", "r") as f:
    user_agents = [line.strip() for line in f]
user_agent = random.choice(user_agents)
chrome_options = Options()
chrome_options.add_argument(f"--user-agent={user_agent}")
driver = uc.Chrome(options=chrome_options)

driver.get("https://www.treasurydirect.gov/auctions/auction-query/")

FIRST_PAGE = 1
LAST_PAGE = 102
for page_num in range(FIRST_PAGE, LAST_PAGE + 1):
    try:
        page_box = driver.find_element(By.CSS_SELECTOR, "input[type='text'][style='height:100%; box-sizing: border-box; text-align: right; width: 36px;'][tabindex='116'].jqx-input.jqx-input-td-2020.jqx-widget-content.jqx-widget-content-td-2020.jqx-grid-pager-input.jqx-grid-pager-input-td-2020.jqx-rc-all.jqx-rc-all-td-2020")
        page_box.clear()
        page_box.send_keys(str(page_num))
        page_box.send_keys(Keys.RETURN)
        time.sleep(2)
        download_button = driver.find_element(By.CSS_SELECTOR, "input[type='button'][value='CSV'][id='csvExport'][role='button'].jqx-rc-all")
        download_button.send_keys(Keys.RETURN)
        time.sleep(2)
    except:
        driver.quit()
