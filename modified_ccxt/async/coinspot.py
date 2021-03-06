# -*- coding: utf-8 -*-

from modified_ccxt.async.base.exchange import Exchange
import hashlib
from modified_ccxt.base.errors import ExchangeError
from modified_ccxt.base.errors import AuthenticationError


class coinspot (Exchange):

    def describe(self):
        return self.deep_extend(super(coinspot, self).describe(), {
            'id': 'coinspot',
            'name': 'CoinSpot',
            'countries': 'AU',  # Australia
            'rateLimit': 1000,
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28208429-3cacdf9a-6896-11e7-854e-4c79a772a30f.jpg',
                'api': {
                    'public': 'https://www.coinspot.com.au/pubapi',
                    'private': 'https://www.coinspot.com.au/api',
                },
                'www': 'https://www.coinspot.com.au',
                'doc': 'https://www.coinspot.com.au/api',
            },
            'api': {
                'public': {
                    'get': [
                        'latest',
                    ],
                },
                'private': {
                    'post': [
                        'orders',
                        'orders/history',
                        'my/coin/deposit',
                        'my/coin/send',
                        'quote/buy',
                        'quote/sell',
                        'my/balances',
                        'my/orders',
                        'my/buy',
                        'my/sell',
                        'my/buy/cancel',
                        'my/sell/cancel',
                    ],
                },
            },
            'markets': {
                'BTC/AUD': {'id': 'BTC', 'symbol': 'BTC/AUD', 'base': 'BTC', 'quote': 'AUD'},
                'LTC/AUD': {'id': 'LTC', 'symbol': 'LTC/AUD', 'base': 'LTC', 'quote': 'AUD'},
                'DOGE/AUD': {'id': 'DOGE', 'symbol': 'DOGE/AUD', 'base': 'DOGE', 'quote': 'AUD'},
            },
        })

    async def fetch_balance(self, params={}):
        response = await self.privatePostMyBalances()
        result = {'info': response}
        if 'balance' in response:
            balances = response['balance']
            currencies = list(balances.keys())
            for c in range(0, len(currencies)):
                currency = currencies[c]
                uppercase = currency.upper()
                account = {
                    'free': balances[currency],
                    'used': 0.0,
                    'total': balances[currency],
                }
                if uppercase == 'DRK':
                    uppercase = 'DASH'
                result[uppercase] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, params={}):
        market = self.market(symbol)
        orderbook = await self.privatePostOrders(self.extend({
            'cointype': market['id'],
        }, params))
        result = self.parse_order_book(orderbook, None, 'buyorders', 'sellorders', 'rate', 'amount')
        result['bids'] = self.sort_by(result['bids'], 0, True)
        result['asks'] = self.sort_by(result['asks'], 0)
        return result

    async def fetch_ticker(self, symbol, params={}):
        response = await self.publicGetLatest(params)
        id = self.market_id(symbol)
        id = id.lower()
        ticker = response['prices'][id]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        return self.privatePostOrdersHistory(self.extend({
            'cointype': self.market_id(symbol),
        }, params))

    def create_order(self, market, type, side, amount, price=None, params={}):
        method = 'privatePostMy' + self.capitalize(side)
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        order = {
            'cointype': self.market_id(market),
            'amount': amount,
            'rate': price,
        }
        return getattr(self, method)(self.extend(order, params))

    async def cancel_order(self, id, symbol=None, params={}):
        raise ExchangeError(self.id + ' cancelOrder() is not fully implemented yet')
        method = 'privatePostMyBuy'
        return await getattr(self, method)({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if not self.apiKey:
            raise AuthenticationError(self.id + ' requires apiKey for all requests')
        url = self.urls['api'][api] + '/' + path
        if api == 'private':
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.json(self.extend({'nonce': nonce}, params))
            headers = {
                'Content-Type': 'application/json',
                'key': self.apiKey,
                'sign': self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
