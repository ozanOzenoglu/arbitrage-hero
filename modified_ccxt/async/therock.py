# -*- coding: utf-8 -*-

from modified_ccxt.async.base.exchange import Exchange
import hashlib
from modified_ccxt.base.errors import ExchangeError


class therock (Exchange):

    def describe(self):
        return self.deep_extend(super(therock, self).describe(), {
            'id': 'therock',
            'name': 'TheRockTrading',
            'countries': 'MT',
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766869-75057fa2-5ee9-11e7-9a6f-13e641fa4707.jpg',
                'api': 'https://api.therocktrading.com',
                'www': 'https://therocktrading.com',
                'doc': [
                    'https://api.therocktrading.com/doc/v1/index.html',
                    'https://api.therocktrading.com/doc/',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'funds/{id}/orderbook',
                        'funds/{id}/ticker',
                        'funds/{id}/trades',
                        'funds/tickers',
                    ],
                },
                'private': {
                    'get': [
                        'balances',
                        'balances/{id}',
                        'discounts',
                        'discounts/{id}',
                        'funds',
                        'funds/{id}',
                        'funds/{id}/trades',
                        'funds/{fund_id}/orders',
                        'funds/{fund_id}/orders/{id}',
                        'funds/{fund_id}/position_balances',
                        'funds/{fund_id}/positions',
                        'funds/{fund_id}/positions/{id}',
                        'transactions',
                        'transactions/{id}',
                        'withdraw_limits/{id}',
                        'withdraw_limits',
                    ],
                    'post': [
                        'atms/withdraw',
                        'funds/{fund_id}/orders',
                    ],
                    'delete': [
                        'funds/{fund_id}/orders/{id}',
                        'funds/{fund_id}/orders/remove_all',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.02 / 100,
                    'taker': 0.2 / 100,
                },
            },
        })

    async def fetch_markets(self):
        markets = await self.publicGetFundsTickers()
        result = []
        for p in range(0, len(markets['tickers'])):
            market = markets['tickers'][p]
            id = market['fund_id']
            base = id[0:3]
            quote = id[3:6]
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privateGetBalances()
        balances = response['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            free = balance['trading_balance']
            total = balance['balance']
            used = total - free
            account = {
                'free': free,
                'used': used,
                'total': total,
            }
            result[currency] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, params={}):
        await self.load_markets()
        orderbook = await self.publicGetFundsIdOrderbook(self.extend({
            'id': self.market_id(symbol),
        }, params))
        timestamp = self.parse8601(orderbook['date'])
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'amount')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.parse8601(ticker['date'])
        symbol = None
        if market:
            symbol = market['symbol']
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
            'close': float(ticker['close']),
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': float(ticker['volume_traded']),
            'quoteVolume': float(ticker['volume']),
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        response = await self.publicGetFundsTickers(params)
        tickers = self.index_by(response['tickers'], 'fund_id')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        ticker = await self.publicGetFundsIdTicker(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_ticker(ticker, market)

    def parse_trade(self, trade, market=None):
        if not market:
            market = self.markets_by_id[trade['fund_id']]
        timestamp = self.parse8601(trade['date'])
        return {
            'info': trade,
            'id': str(trade['id']),
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': trade['price'],
            'amount': trade['amount'],
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetFundsIdTrades(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response['trades'], market)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        response = await self.privatePostFundsFundIdOrders(self.extend({
            'fund_id': self.market_id(symbol),
            'side': side,
            'amount': amount,
            'price': price,
        }, params))
        return {
            'info': response,
            'id': str(response['id']),
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        return await self.privateDeleteFundsFundIdOrdersId(self.extend({
            'id': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            self.check_required_credentials()
            nonce = str(self.nonce())
            auth = nonce + url
            headers = {
                'X-TRT-KEY': self.apiKey,
                'X-TRT-NONCE': nonce,
                'X-TRT-SIGN': self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha512),
            }
            if query:
                body = self.json(query)
                headers['Content-Type'] = 'application/json'
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if 'errors' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
