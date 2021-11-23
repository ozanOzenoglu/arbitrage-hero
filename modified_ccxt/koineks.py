# -*- coding: utf-8 -*-

from modified_ccxt.base.exchange import Exchange
from base.crypto_engine.setting_db.request_info import RequestInfo, RequestType
from modified_ccxt.base.errors import ExchangeError
from modified_ccxt.base.errors import InvalidNonce
from modified_ccxt.base.errors import InsufficientFunds
from modified_ccxt.base.errors import InvalidOrder
from modified_ccxt.base.errors import OrderNotFound
from modified_ccxt.base.errors import CancelPending
from modified_ccxt.base.errors import DDoSProtection
from modified_ccxt.base.errors import ExchangeNotAvailable
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine import symbols
import requests
import json
import time


class koineks(Exchange):
    balance_age_threshold = 25 * 1000  # s
    max_age_threshold = 60 * 1000  #  if age of a info is more than 60 secs it's old and un acceptable .!
    fresh_age_threshold = 15 * 1000  # if age of a info is more than 15 secs it's not fresh ! and shouldn't be use for arbitrage operations!
    koineks_order_book_url = "https://ozenoglu.com/order_books/koineks.json"

    def describe(self):
        return self.deep_extend(super(koineks, self).describe(), {
            'id': 'koineks',
            'name': 'koineks',
            'countries': 'US',
            'version': '0',
            'rateLimit': 3000,
            'hasCORS': False,
            # obsolete metainfo interface
            'hasFetchTickers': True,
            'hasFetchOHLCV': False,
            'hasFetchOrder': False,
            'hasFetchOpenOrders': False,
            'hasFetchClosedOrders': False,
            'hasFetchOrderBook': True,
            'hasFetchMyTrades': False,
            'hasWithdraw': False,
            # new metainfo interface
            'has': {
                'hasFetchOrderBook': True,
                'fetchTickers': True,
                'fetchOHLCV': False,
                'fetchOrder': False,
                'fetchOpenOrders': False,
                'fetchClosedOrders': False,
                'fetchMyTrades': False,
                'withdraw': False,
            },
            'marketsByAltname': {},
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': '1440',
                '1w': '10080',
                '2w': '21600',
            }, 'fees': {
                'trading': {
                    'maker': 0.20 / 100,
                    'taker': 0.30 / 100,
                },
                'funding': {
                    'withdraw': {
                        'TRY': 3.0,
                        # 'USD': None,
                        # 'EUR': None,
                        # 'RUB': None,
                        # 'GBP': None,
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
                    },
                    'deposit': {
                        # 'USD': amount => amount * 0.035 + 0.25,
                        # 'EUR': amount => amount * 0.035 + 0.24,
                        # 'RUB': amount => amount * 0.05 + 15.57,
                        # 'GBP': amount => amount * 0.035 + 0.2,
                        'BTC': 0.0,
                        'ETH': 0.0,
                        'BCH': 0.0,
                        'DASH': 0.0,
                        'BTG': 0.0,
                        'ZEC': 0.0,
                        'XRP': 0.0,
                        'XLM': 0.0,
                    },
                },
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766599-22709304-5ede-11e7-9de1-9f33732e1509.jpg',
                'api': 'https://koineks.com/info/api',
                'www': 'https://www.koineks.com',
                'doc': [
                    'None',
                    'None',
                ],
                'fees': 'https://www.kraken.com/en-us/help/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'Ticker',
                    ],
                }

            },
        })

    def cost_to_precision(self, symbol, cost):
        return self.truncate(float(cost), self.markets[symbol]['precision']['price'])

    def fee_to_precision(self, symbol, fee):
        return self.truncate(float(fee), self.markets[symbol]['precision']['amount'])

    def handle_errors(self, code, reason, url, method, headers, body):
        if body.find('Invalid nonce') >= 0:
            raise InvalidNonce(self.id + ' ' + body)
        if body.find('Insufficient funds') >= 0:
            raise InsufficientFunds(self.id + ' ' + body)
        if body.find('Cancel pending') >= 0:
            raise CancelPending(self.id + ' ' + body)
        if body.find('Invalid arguments:volume') >= 0:
            raise InvalidOrder(self.id + ' ' + body)

    def fetch_markets(self):

        raise NotImplementedError("Not Implemented Yet")

    def append_inactive_markets(self, result=[]):

        raise NotImplementedError("Not Implemented Yet")

    def is_update_time_fresh(self, update_time, symbol, age: int = -1):
        if age == -1:
            age = koineks.max_age_threshold

        now = int(round(time.time() * 1000))
        difference = now - update_time
        if (difference > age):  #  if more than 120 secs
            debug("info data {:s} old as  {:d} secs".format(str(symbol), int(difference / 1000)))
            return False
        else:
            debug("info data {:s} new  as  {:d} secs".format(str(symbol), int(difference / 1000)))
            return True

    def is_server_alive(self):
        return True  # TODO implement this func

    def get_order_book_from_server(self, symbol: str):
        symbol = str(symbol).upper()
        if self.is_server_alive():
            response_as_dict = None
            try:
                my_dict = {"private_key": "blabla", "event": "fetch_koineks_orderbook", "data": "my_data_info"}
                my_dict_str = json.dumps(my_dict)

                response = requests.get(koineks.koineks_order_book_url, data=my_dict_str)
                response_as_dict = json.loads(response.content.decode("UTF-8"))
            except Exception as e:
                error("error during fetching data from server {:s}".format(str(e)))
            try:
                if (response_as_dict != None):
                    return response_as_dict.__getitem__(symbol)
                else:
                    return None
            except Exception as e:
                error("Error during fetching order book from server api: {:s}".format(str(e)))

    def get_order_book_from_file(self, symbol: str):
        symbol = str(symbol).upper()
        data = None
        try:
            with open(symbols.KOINEKS_ORDER_BOOK_FILE, 'r') as arbitrage_pairs_file:
                data = json.load(arbitrage_pairs_file)
                return data.__getitem__(symbol)
        except Exception as e:
            error("Unexcepted Exception is during get_order_book_from_file : {:s}".format(str(e)))

    def fetch_order_book(self, symbol, params={}):
        try:
            need_fresh = params.__getitem__('need_fresh')
        except Exception as e:
            need_fresh = False
        try:
            from_file = params.__getitem__('from_file')
        except Exception as e:
            from_file = False

        if need_fresh is not None:
            if isinstance(need_fresh, bool) is not True:
                try:
                    if str(need_fresh).upper() == "TRUE":
                        need_fresh = True
                    elif str(need_fresh).upper() == "FALSE":
                        need_fresh = False
                except Exception as e:
                    raise Exception(
                        "Given params is not recgonized as valid param , give a bool type or string form. WTF?")
        else:
            need_fresh = False

        try:
            if (str(symbol).__contains__('/')):
                symbol = str(symbol).split('/')[0]
            debug("koineks api fetch_order_book CALL for {:s}".format(str(symbol)))
            order_book = None
            if (self.is_server_alive() and from_file is not True):
                debug("SERVER IS ALIVE GET ORDER BOOK FROM SERVER")
                order_book = self.get_order_book_from_server(symbol)
            if (order_book == None):
                if symbols.LOCAL_ORDERBOOK_SUPPORT:
                    order_book = self.get_order_book_from_file(symbol)
                else:
                    error('we couldnt fetch order book from server and from file due to no support for local orderbook')

            if order_book == None:
                raise Exception("Order book could not fetched!")
            update_time = order_book.__getitem__('update_time')
            if need_fresh:
                valid = self.is_update_time_fresh(update_time, symbol, koineks.fresh_age_threshold)
            else:
                valid = self.is_update_time_fresh(update_time, symbol, koineks.max_age_threshold)

            if valid is not True:
                raise Exception('{:s} order book is old, please check koineks service'.format(str(symbol)))

            debug("koineks api fetch_order_book  RETURN {:s}".format(str(symbol)))
            return self.parse_order_book(order_book)
        except Exception as e:
            if str(e).__contains__("order book is old"):
                warn(str(e))  # if koineks service helper is alive , we will request a urgent fetch for that currency.
            else:
                error("Koineks Api call exception : {:s}".format(str(e)))
            raise e

    def parse_ticker(self, ticker, symbol: str):
        timestamp = self.milliseconds()

        ticker = json.loads(ticker)  #  convert str to dict
        symbols = symbol.split('/')
        base = symbols[1]
        symbol = symbols[0]
        try:
            symbol_info = ticker.__getitem__(symbol)
            result = {
                'symbol': symbol,
                'timestamp': timestamp,
                'datetime': self.iso8601(timestamp),
                'high': float(symbol_info.__getitem__('high')),
                'low': float(symbol_info.__getitem__('low')),
                'bid': float(symbol_info.__getitem__('bid')),
                'ask': float(symbol_info.__getitem__('ask')),
                'open': None,
                'close': None,
                'first': None,
                'last': None,
                'change': None,
                'percentage': None,
                'average': None,
                'baseVolume': 'TRY',
                'info': ticker,
            }
            return result

        except KeyError as e:
            raise e  #  raise here modified_ccxt errors

    def fetch_tickers(self, symbols=None, params={}):
        raise NotImplementedError("Not implemented yet")

    def fetch_ticker(self, symbol, params={}):

        url = "https://koineks.com/ticker"
        r = requests.get(url)
        return self.parse_ticker(r.text, symbol)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):

        raise NotImplementedError("Not Implemented Yet")

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def parse_trade(self, trade, market=None):

        raise NotImplementedError("Not Implemented Yet")

    def fetch_trades(self, symbol, since=None, limit=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def get_balance_from_file(self):
        try:
            with open(symbols.KOINEKS_BALANCE_FILE, 'r') as balance_file:
                data = json.load(balance_file)
                return data
        except Exception as e:
            error("Unexcepted Exception is during get_order_book_from_file : {:s}".format(str(e)))
            error(json.dumps(data))
            raise Exception("Unexcepted Exception is handled!")

    def private_fetch_all_balance(self, try_count: int = 0):

        try_count = try_count + 1
        if try_count > 5:            raise Exception(
            "Tried {:d} already and couldn't fetch balance all".format(try_count))
        debug("try_cound : {:d}".format(int(try_count)))

        balance_info = self.get_balance_from_file()

        balances = {}
        currencies = symbols.KOINEKS_MARKETS
        currencies.append('TRY')

        for currency in symbols.KOINEKS_MARKETS:
            symbol_info = balance_info.__getitem__(currency)
            last_update = symbol_info.__getitem__('update_time')

            if (self.is_update_time_fresh(last_update, currency, koineks.balance_age_threshold) == True):
                balance = float(symbol_info.__getitem__('balance'))
                balances.update({currency: balance})
            else:
                error("Old info , need update!")

                fetch_balance_request = RequestInfo("koineks", RequestType.GET_ALL_BALANCE)
                fetch_balance_request.set_log_file_name("fetch_all_balance_bitte")
                fetch_balance_request.push_request()
                time.sleep(5 * try_count)  # wait koineks_service populate info file..

                balances = self.private_fetch_all_balance(try_count)
                return balances

        return balances

    def fetch_balance(self, params={}):

        all_balance_info = self.private_fetch_all_balance()

        result = {'info': all_balance_info}

        for currency in symbols.KOINEKS_MARKETS:
            balance = float(all_balance_info.__getitem__(currency))
            account = {
                'free': balance,
                'used': 0.0,
                'total': balance,
            }
            result[currency] = account

        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price, params={}):

        result_type = ""
        if side == "buy":
            if (type == "limit"):
                result_type = "limit_buy"
            elif (type == "market"):
                result_type = "market_buy"
            else:
                raise Exception("Incorrect type for buy : {:s}".format(str(type)))

        elif side == "sell":
            if (type == "limit"):
                result_type = "limit_sell"
            elif type == "market":
                result_type = "market_sell"
            else:
                raise Exception("Incorrect type for sell : {:s}".format(str(type)))

        if str(symbol).__contains__('/'):
            symbol = symbol.split('/')[0]

        if side == "buy":

            buy_request = RequestInfo("koineks", RequestType.BUY, symbol)
            buy_request.set_amount(amount)
            buy_request.set_price(price)
            log_name = symbol + "_buy"
            buy_request.set_log_file_name(log_name)
            buy_request.push_request()
        elif side == "sell":
            sell_request = RequestInfo("koineks", RequestType.SELL, symbol)
            sell_request.set_amount(amount)
            sell_request.set_price(price)
            sell_request.set_log_file_name(symbol + "_sell")
            sell_request.push_request()

        return {'type': result_type, 'price': price, 'amount': amount, 'symbol': symbol}

    def find_market_by_altname_or_id(self, id):

        raise NotImplementedError("Not Implemented Yet")

    def parse_order(self, order, market=None):

        raise NotImplementedError("Not Implemented Yet")

    def parse_orders(self, orders, market=None):

        raise NotImplementedError("Not Implemented Yet")

    def fetch_order(self, id, symbol=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def cancel_order(self, id, symbol=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def withdraw(self, currency, amount, address, params={}):

        withdraw_request = RequestInfo("koineks", RequestType.WITHDRAW, currency)

        log_file_name = params.__getitem__('log_file_name') + "_withdraw"
        withdraw_request.set_log_file_name(log_file_name)
        tag = ""
        withdraw_request.set_destination(address)
        withdraw_request.set_amount(amount)

        if (str(currency).__contains__('XRP') or str(currency).__contains__('XLM')):
            tag = params.__getitem__('tag')
            withdraw_request.set_tag(tag)
        withdraw_request.push_request()
        return {'type': 'withdraw', 'amount': amount, 'destination': address, 'tag': tag, 'symbol': currency}

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):

        raise NotImplementedError("Not Implemented Yet")

    def nonce(self):
        return self.milliseconds()

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'error' in response:
            numErrors = len(response['error'])
            if numErrors:
                for i in range(0, len(response['error'])):
                    if response['error'][i] == 'EService:Unavailable':
                        raise ExchangeNotAvailable(self.id + ' ' + self.json(response))
                    if response['error'][i] == 'EService:Busy':
                        raise DDoSProtection(self.id + ' ' + self.json(response))
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response



