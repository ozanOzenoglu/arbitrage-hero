from base.crypto_engine.utils.config_manager import Config
from base.crypto_engine.engine.event import Consumer , Event
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.engine.transaction_engine import TransactionEngine , Operation
from sys import argv

Config.load_market_configs()
markets = Config.get_markets_from_config()

if (len(argv) > 2):
    market_name = argv[1]
else:
    market_name = "btcturk"

market = markets.__getitem__(market_name)

class marketLooker(Consumer):


    def do_it(self):
        fetch = Operation.create_fetch_market_price(market, 'ETH', 1, 60)
        fetch.add_consumer(self)
        engine = TransactionEngine()
        op_list = []
        op_list.append(fetch)
        engine.create_and_add_transaction(op_list)
        engine.start_engine()

    def handle_event(self,event:Event):
        if event.get_type() == Event.FETCH_MARKET_PRICE:
            data = event.get_data()
            if data == "Operation is Failed":
                android_alarm("Server is down")
                self.do_it()
            else:
                android_alarm("Server is up !")
                self.do_it()



looker = marketLooker()
looker.do_it()
