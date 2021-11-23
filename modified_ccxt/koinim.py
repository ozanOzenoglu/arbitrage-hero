# -*- coding: utf-8 -*-

from modified_ccxt.base.exchange import Exchange
import base64
import hashlib
import math
from modified_ccxt.base.errors import ExchangeError
from modified_ccxt.base.errors import InvalidNonce
from modified_ccxt.base.errors import InsufficientFunds
from modified_ccxt.base.errors import InvalidOrder
from modified_ccxt.base.errors import OrderNotFound
from modified_ccxt.base.errors import CancelPending
from modified_ccxt.base.errors import DDoSProtection
from modified_ccxt.base.errors import ExchangeNotAvailable
import requests
import json


class koinim (Exchange):

    def describe(self):
        return self.deep_extend(super(koinim, self).describe(), {
            'id': 'koinim',
            'name': 'koinim',
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
            'hasFetchMyTrades': False,
            'hasWithdraw': False,
            # new metainfo interface
            'has': {
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
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766599-22709304-5ede-11e7-9de1-9f33732e1509.jpg',
                'api': 'https://koinim.com/info/api',
                'www': 'https://www.koinim.com',
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

    def fetch_order_book(self, symbol, params={}):
        raise NotImplementedError("Not Implemented Yet")

    def parse_ticker(self, ticker, symbol:str):
        timestamp = self.milliseconds()

        ticker = json.loads(ticker) # convert str to dict
        symbols = symbol.split('/')
        base = symbols[1]
        symbol = symbols[0]
        try:
            symbol_info = ticker
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
                'last': float(symbol_info.__getitem__('last_order')),
                'change': float(symbol_info.__getitem__('change_rate')),
                'percentage': None,
                'average': float(symbol_info.__getitem__('avg')),
                'baseVolume': 'TRY',
                'info': ticker,
            }


            return result

        except KeyError as e:
            raise e # raise here modified_ccxt errors




    def fetch_tickers(self, symbols=None, params={}):
        raise NotImplementedError("Not implemented yet")


    def fetch_ticker(self, symbol, params={}):

        second = symbol.split('/')[1]
        first = symbol.split('/')[0]
        if (first == "BTC"):
            first = ""

        url = "https://koinim.com/ticker/" + str(first).lower()
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

    def fetch_balance(self, params={}):

        raise NotImplementedError("Not Implemented Yet")

    def create_order(self, symbol, type, side, amount, price=None, params={}):

        raise NotImplementedError("Not Implemented Yet")

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

        raise NotImplementedError("Not Implemented Yet")

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
