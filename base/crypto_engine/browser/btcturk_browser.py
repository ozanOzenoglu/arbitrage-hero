from browser import Browser


class BtcturkBrowser(Browser):

    def __init__(self):
        print("btcturk constructor")

    def login(self):
        pass

    def fetch_balance(self, symbol: str):
        pass

    def go_to_market(self, market: str):
        pass

    def fetch_order_book(symbol: str):
        pass

    def withdraw(self, currency: str, amount: float, address: str, tag: str = ""):
        pass

    def get_ss(self):
        pass

    def buy_request(self, symbol: str, amount: float, price: float):
        pass

    def sell_request(self, symbol: str, amount: float, price: float):
        pass