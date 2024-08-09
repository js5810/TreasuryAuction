import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd
import glob
from utils import *

class TreasurySecurity:

    def __init__(self):
        pass

    def random_user_agent(self) -> str:
        """Give a random user agent from the list to include in request"""
        with open("../metadata/Chrome.txt", "r") as f:
            user_agents = [line.strip() for line in f]
        user_agent = random.choice(user_agents)
        return user_agent

    def download_tables(self) -> None:
        """Navigates through Treasury website to gather data"""
        user_agent = self.random_user_agent()
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

    def combine_tables(self) -> None:
        """Merge all data into one large table"""
        files = glob.glob("../data/*.csv")
        df_list = []
        for file in files:
            df = pd.read_csv(file, index_col=False)
            df_list.append(df)

        combined_df = pd.concat(df_list, axis=0, ignore_index=False)
        combined_df.sort_values(by="Auction Date", inplace=True)
        combined_df.dropna(subset="Price per $100", inplace=True)
        #combined_df.to_csv("combined_data.csv", index=False)
    
    def get_all_CUSIP(self, term: str) -> list[str]:
        """Extract all CUSIP of any debt security ever sold"""
        df = pd.read_csv("../data/combined_auction_data.csv")
        return [cusip for cusip in df[df["Security Term"] == term]["CUSIP"]]  # still need to distinugish TIPS

    def calculate_YTM(self, auction: dict) -> float:
        """Back-engineer the auction's Yield to Maturity from price, different formula for bills vs notes/bonds"""
        return
    
    def auction_data(self) -> dict[dict]:
        """Return info on all auctions that ever took place for this security"""
        return

    def market_yield_added(self) -> list:
        return

    def create_graph(self) -> None:
        """Make a graph of yield for a specific term (10-Year, 30-Year, etc.)"""
        return