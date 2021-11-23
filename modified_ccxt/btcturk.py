# -*- coding: utf-8 -*-
import time, base64, hmac, requests, json
from modified_ccxt.base.exchange import Exchange
import hashlib
from modified_ccxt.base.errors import ExchangeError
from base.services.btcturk_service import BtcTurkService
from base.crypto_engine.setting_db.request_info import RequestInfo,RequestType
from base.crypto_engine.MessageApi.debug import *
import  time
class btcturk (Exchange):

    def describe(self):
        return self.deep_extend(super(btcturk, self).describe(), {
            'id': 'btcturk',
            'name': 'BTCTurk',
            'countries': 'TR',  # Turkey
            'rateLimit': 1000,
            'hasCORS': True,
            'hasFetchTickers': True,
            'hasWithdraw' : True,
            'hasFetchOHLCV': True,
            'timeframes': {
                '1d': '1d',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27992709-18e15646-64a3-11e7-9fa2-b0950ec7712f.jpg',
                'api': 'https://api.btcturk.com/api/v2', #https://api.btcturk.com/api/v2 , https://api.btcturk.com/api/v1/users
                'apiv1' : 'https://api.btcturk.com/api/v1/users',
                'www': 'https://www.btcturk.com',
                'doc': 'https://github.com/BTCTrader/broker-api-docs',
            },
            'api': {
                'public': {
                    'get': [
                        'ohlcdata',  # ?last=COUNT
                        'orderbook',
                        'ticker',
                        'trades',   # ?last=COUNT(max 50)
                    ],
                },
                'private': {
                    'get': [
                        'balance',
                        'openOrders',
                        'userTransactions',  # ?offset=0&limit=25&sort=asc
                    ],
                    'post': [
                        'exchange',
                        'cancelOrder',
                        'exchange',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.20 / 100,
                    'taker': 0.30 / 100,
                },
                'funding': {
                    'withdraw': {
                        'TRY': 0,
                        'BTC': 0.0007,
                        'ETH': 0.005,
                        'USDT': 3.0,
                        'LTC': 0.01,
                        'DOGE': 2,
                        'BCH': 0.001,
                        'DASH': 0.002,
                        'BTG': 0.001,
                        'ZEC': 0.001,
                        'ETC': 0.003,
                        'XEM': 1,
                        'XLM': 0.3,
                        'XRP': 1,
                        'ADA': 1,
                        'NEO': 0,
                        'DOT': 0.1,
                        'EOS': 0.1,
                        'TRX': 2.5,
                        'USDC': 5,
                        'USDT': 1,
                        'XTZ': 1,
                        'ATOM': 0.005,
                        'LINK': 0.33,
                        
                    },
                    'deposit': {
                        'BTC': 0.0,
                        'ETH': 0.0,
                        'BCH': 0.0,
                        'DASH': 0.0,
                        'BTG': 0.0,
                        'ZEC': 0.0,
                        'XRP': 0.0,
                        'XLM': 0.0,
                        'ADA': 1,
                        'NEO': 0,
                        'DOT': 0,
                        'EOS': 0,
                        'TRX': 0,
                        'USDC': 0,
                        'USDT': 0,
                        'XTZ': 0,
                        'ATOM': 0,
                        'LINK': 0,
                    },
                },
            },
            'markets': {
                'XRP/TRY': {'id': 'XRPTRY', 'symbol': 'XRP/TRY', 'base': 'BTC', 'quote': 'TRY', 'maker': 0.002,'taker': 0.0035},
                'LTC/TRY': {'id': 'LTCTRY', 'symbol': 'LTC/TRY', 'base': 'BTC', 'quote': 'TRY', 'maker': 0.002,'taker': 0.0035},
                'XLM/TRY': {'id': 'XLMTRY', 'symbol': 'XLM/TRY', 'base': 'BTC', 'quote': 'TRY', 'maker': 0.002,'taker': 0.0035},
                'BTC/TRY': {'id': 'BTCTRY', 'symbol': 'BTC/TRY', 'base': 'BTC', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'ETH/TRY': {'id': 'ETHTRY', 'symbol': 'ETH/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'ETH/BTC': {'id': 'ETHBTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'maker': 0.002, 'taker': 0.0035},
                'ADA/TRY': {'id': 'ADATRY', 'symbol': 'ADA/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'NEO/TRY': {'id': 'NEOTRY', 'symbol': 'NEO/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'DOT/TRY': {'id': 'DOTTRY', 'symbol': 'DOT/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'EOS/TRY': {'id': 'EOSTRY', 'symbol': 'EOS/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'TRX/TRY': {'id': 'TRXTRY', 'symbol': 'TRX/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'USDC/TRY': {'id': 'USDCTRY', 'symbol': 'USDC/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'USDT/TRY': {'id': 'USDTTRY', 'symbol': 'USDT/TRY', 'base': 'TRY', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'XTZ/TRY': {'id': 'XTZTRY', 'symbol': 'XTZ/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'ATOM/TRY': {'id': 'ATOMTRY', 'symbol': 'ATOM/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
                'LINK/TRY': {'id': 'LINKTRY', 'symbol': 'LINK/TRY', 'base': 'ETH', 'quote': 'TRY', 'maker': 0.002, 'taker': 0.0035},
            },
        })




    def withdraw(self, currency, amount, address, params={}):
        tag = ""
        request = RequestInfo(RequestType.WITHDRAW, currency)
        request.set_destination(address)
        request.set_amount(amount)

        try:
            log_file_path = params.__getitem__('log_file_name')
            request.set_log_file_name(log_file_path)
        except Exception as e:
            debug("No log file path is given!")

        if (currency == "XRP"):
            try:
                tag = params.__getitem__('tag')
                request.set_tag(tag)
            except Exception as e:
                error("Tag is not given !")
                raise Exception("No Tag given with destination address")

        if (BtcTurkService.is_service_healthy() is not True):
            raise Exception("BtcturkService is not working")
        ret = BtcTurkService.push_request(request)
        if (ret != -1) :
            return {'type': 'withdraw', 'amount': amount, 'destination': address, 'tag': tag, 'symbol': currency}

    
    def fetch_balance(self, params={}):
        got_response = False
        response_get_try_count = 0

        while got_response == False:
            try:
                response_get_try_count = response_get_try_count + 1
                response = self.privateGetBalance()
                if response.__getitem__('success') is not True:
                    raise Exception(response.__getitem__('Data'))
                got_response = True
            except Exception as e :
                if response_get_try_count > 5 :
                    raise Exception("Error fetching btcturk balance: {:s}".format(str(e)))
                else:
                    time.sleep(1)

        result = {'info': response}
        balance_info = response.__getitem__('data')
        try_info = balance_info[0]
        btc_info = balance_info[1]
        eth_info = balance_info[2]
        xrp_info = balance_info[3]
        usdt_info = balance_info[5]
        xlm_info = balance_info[6]
        
        xlm_balance = {
            'free': xlm_info.__getitem__('free'),
            'used': xlm_info.__getitem__('locked'),
            'total': xlm_info.__getitem__('balance'),
        }
        usdt_balance = {
            'free': usdt_info.__getitem__('free'),
            'used': usdt_info.__getitem__('locked'),
            'total': usdt_info.__getitem__('balance'),
        }
        
        btc_balance = {
            'free': btc_info.__getitem__('free'),
            'used': btc_info.__getitem__('locked'),
            'total': btc_info.__getitem__('balance'),
        }
        try_balance = {
            'free': try_info.__getitem__('free'),
            'used': try_info.__getitem__('locked'),
            'total': try_info.__getitem__('balance'),
        }
        eth_balance = {
            'free': eth_info.__getitem__('free'),
            'used': eth_info.__getitem__('locked'),
            'total': eth_info.__getitem__('balance'),
        }
        xrp_balance = {
            'free': xrp_info.__getitem__('free'),
            'used': xrp_info.__getitem__('locked'),
            'total': xrp_info.__getitem__('balance'),
        }
       
        symbol = self.symbols[0]
        market = self.markets[symbol]

        result['BTC'] = btc_balance
        result['TRY'] = try_balance
        result['ETH'] = eth_balance
        result['XRP'] = xrp_balance
        result['XLM'] = xlm_balance
        result['USDT'] = usdt_balance

        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = self.publicGetOrderbook(self.extend({
            'pairSymbol': market['id'], #market_id burada BTC/TRY geliyor bıuunu BTC_TRY yapacaz
        }, params))
        orderbook = orderbook['data']
        timestamp = int(orderbook['timestamp'] * 1000)
        return self.parse_order_book(orderbook, timestamp)

    def parse_ticker(self, ticker, market=None):
        symbol = None
        if market:
            symbol = market['symbol']
        timestamp = int(ticker['timestamp']) * 1000
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': float(ticker['average']),
            'baseVolume': float(ticker['volume']),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        result = {}
        for i in range(0, len(tickers)):
            ticker = tickers[i]
            symbol = ticker['pair']
            market = None
            if symbol in self.markets_by_id:
                market = self.markets_by_id[symbol]
                symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        tickers = self.fetch_tickers()
        result = None
        if symbol in tickers:
            result = tickers[symbol]
        return result

    def parse_trade(self, trade, market):
        timestamp = trade['date'] * 1000
        return {
            'id': trade['tid'],
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        # maxCount = 50
        response = self.publicGetTrades(self.extend({
            'pairSymbol': market['id'],
        }, params))
        return self.parse_trades(response, market)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        timestamp = self.parse8601(ohlcv['Time'])
        return [
            timestamp,
            ohlcv['Open'],
            ohlcv['High'],
            ohlcv['Low'],
            ohlcv['Close'],
            ohlcv['Volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {}
        if limit:
            request['last'] = limit
        response = self.publicGetOhlcdata(self.extend(request, params))
        return self.parse_ohlcvs(response, market, timeframe, since, limit)
    
    def authorize(self):
        apiKey = "d572e580-c58a-4a09-a37e-dce777ebae06"
        apiSecret = "d1nOaX+YcWLjL0cq1pTUTkGfIViVuQVo"
        apiSecret = base64.b64decode(apiSecret)

        stamp = str(int(time.time())*1000)
        data = "{}{}".format(apiKey, stamp).encode("utf-8")
        signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}
        return headers

    def convert_symbol(self, symbol):
        symbol_pair = str(symbol).split("/")
        if(len(symbol_pair)== 1):
            symbol = symbol + "_TRY"
        else:
            symbol = symbol_pair[0] + "_" + symbol_pair[1]
        return symbol
    
    def market_buy(self, symbol, amount):
        base = "https://api.btcturk.com"
        method = "/api/v1/order"
        uri = base+method
        symbol = self.convert_symbol(symbol)

        params={"quantity": int(amount), "newOrderClientId":"BtcTurk Python API Test", "orderMethod":"market", "orderType":"buy", "pairSymbol":symbol}
        headers = self.authorize()      

        result = requests.post(url=uri, headers=headers, json=params)
        result = result.json()
        print(json.dumps(result, indent=2))
        return result
    
    def market_sell(self, symbol, amount):
        base = "https://api.btcturk.com"
        method = "/api/v1/order"
        uri = base+method
        symbol = self.convert_symbol(symbol)

        headers = self.authorize()        
        params={"quantity": int(amount),"price": 0,"stopPrice": 0, "newOrderClientId":"BtcTurk Python API Test", "orderMethod":"market", "orderType":"sell", "pairSymbol":symbol}

        result = requests.post(url=uri, headers=headers, json=params)
        result = result.json()
        print(json.dumps(result, indent=2))
        return result
    
    def limit_sell(self, symbol, amount, price):
        base = "https://api.btcturk.com"
        method = "/api/v1/order"
        uri = base+method

        apiKey = "d572e580-c58a-4a09-a37e-dce777ebae06"
        apiSecret = "d1nOaX+YcWLjL0cq1pTUTkGfIViVuQVo"
        apiSecret = base64.b64decode(apiSecret)

        stamp = str(int(time.time())*1000)
        data = "{}{}".format(apiKey, stamp).encode("utf-8")
        signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
        signature = base64.b64encode(signature)
        headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}

        params={"quantity": float(amount),"price": float(price),"stopPrice": 0, "newOrderClientId":"BtcTurk Python API Test", "orderMethod":"limit", "orderType":"sell", "pairSymbol":"XLM_TRY"}

        result = requests.post(url=uri, headers=headers, json=params)
        result = result.json()
        print(result)
        try:
            result = result.__getitem__('success')
            if(result == True):
                result = {"success":True,"symbol":symbol, "amount": amount, "price": price}
            else:
                result = {"success":False,"symbol":symbol, "amount": amount, "price": price}
            return result
        except Exception as e:
            error("Error during limit sell Ex: {:s}".format(str(e)))
            return {"success":False,"symbol":symbol, "amount": amount, "price": price}
        

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        result = None
        if(type == "market"):
            if(side == "buy"):
                result = self.market_buy(symbol,amount)
            else:
                result = self.market_sell(symbol,amount)
        if(type == "limit"):
            if(side == "buy"):
                result = self.limit_buy(symbol,amount,price)
            else:
                result = self.limit_sell(symbol,amount,price)
        
        return result

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + path
        if path == "balance":
            path = "balances"
            url = self.urls['apiv1'] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            apiKey = "d572e580-c58a-4a09-a37e-dce777ebae06"
            apiSecret = "d1nOaX+YcWLjL0cq1pTUTkGfIViVuQVo"
            apiSecret = base64.b64decode(apiSecret)
            stamp = str(int(time.time())*1000)
            data = "{}{}".format(apiKey, stamp).encode("utf-8")
            signature = hmac.new(apiSecret, data, hashlib.sha256).digest()
            signature = base64.b64encode(signature)
            headers = {"X-PCK": apiKey, "X-Stamp": stamp, "X-Signature": signature, "Content-Type" : "application/json"}

            
            #nonce = str(self.nonce())
            #body = self.urlencode(params) if params else None
            #secret = self.base64ToString(self.secret)
            #auth = str(self.apiKey + nonce)
            #auth = auth.encode("utf-8")
            #try:
            #    headers = {
            #        'X-PCK': self.apiKey,
            #        'X-Stamp': str(nonce),
            #        'X-Signature': self.hmac(secret, auth, hashlib.sha256, 'base64'),
            #        'Content-Type': 'application/json',
            #    }
            #except Exception as e:
            #    print("Exception {:s}".format(str(e)))
                
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    @staticmethod
    def base64ToString(s):
        import base64
        return base64.b64decode(s)