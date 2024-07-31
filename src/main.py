from treasury_security import TreasurySecurity
from treasury_note_bond import TreasuryNoteBond
from treasury_bill import TreasuryBill

if __name__ == "__main__":
    #auction_obj = TreasuryNoteBond("10-Year", "No")
    #auction_obj.create_graph()

    auction_obj = TreasuryBill("13-Week")
    print(auction_obj.auction_data("912796Q28"))