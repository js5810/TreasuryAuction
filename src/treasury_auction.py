import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd
import glob
import requests
from utils import *


class TreasuryAuction:

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
    
    def get_all_CUSIP(self) -> list[str]:
        """Extract all CUSIP of any debt security ever sold"""
        df = pd.read_csv("../data/combined_table.csv")
        return [cusip for cusip in df["CUSIP"]]


    def calculate_YTM(self, price: float, coupon_rate: float, maturity_days: float) -> float:
        """Back-engineer the auction's Yield to Maturity from price, coupon rate, and time to maturity"""
        return
    

    def auction_data(self, cusip: str) -> list[list[float]]:
        """Retrieve the price, coupon rate, and low/median/high bids for yield from all auctions that ever took place for this debt security"""
        user_agent = self.random_user_agent()
        headers = {
            "User-Agent": user_agent
        }
        response_json = requests.get(url=f"https://www.treasurydirect.gov/TA_WS/securities/search?cusip={cusip}&callback=?&format=json", headers=headers).json()
        relevant_data = {}
        for auction in response_json:  # each dictionary object is a separate auction day
            try:
                auction_date = auction["auctionDate"]
                relevant_data[auction_date] = {}
            except ValueError as e:
                continue
            try:
                price_per_100 = float(auction["pricePer100"])
                relevant_data[auction_date]["price"] = price_per_100
            except ValueError as e:
                continue
            try:
                coupon_rate = float(auction["interestRate"])  # treasury's API calls coupon rate the interest rate
                relevant_data[auction_date]["coupon_rate"] = coupon_rate
            except ValueError as e:
                continue
            try:
                maturity_days = auction["securityTerm"]
                relevant_data[auction_date]["maturity"] = maturity_days
            except ValueError as e:
                continue
            try:
                lowest_YTM = float(auction["lowYield"])
                relevant_data[auction_date]["low_bid"] = lowest_YTM
            except ValueError as e:
                continue
            try:
                highest_YTM = float(auction["highYield"])
                relevant_data[auction_date]["high_bid"] = highest_YTM
            except ValueError as e:
                continue
            try:
                median_YTM = float(auction["averageMedianYield"])
                relevant_data[auction_date]["median_bid"] = median_YTM
            except ValueError as e:
                continue

        return relevant_data

            

    def create_graph(self) -> float:
        cusip_list = self.get_all_CUSIP()
        for cusip in cusip_list:
            all_auctions = self.auction_data(cusip)
            for auction in all_auctions:
                self.calculate_YTM