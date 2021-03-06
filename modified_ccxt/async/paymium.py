# -*- coding: utf-8 -*-

from modified_ccxt.async.base.exchange import Exchange
from modified_ccxt.base.errors import ExchangeError


class paymium (Exchange):

    def describe(self):
        return self.deep_extend(super(paymium, self).describe(), {
            'id': 'paymium',
            'name': 'Paymium',
            'countries': ['FR', 'EU'],
            'rateLimit': 2000,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27790564-a945a9d4-5ff9-11e7-9d2d-b635763f2f24.jpg',
                'api': 'https://paymium.com/api',
                'www': 'https://www.paymium.com',
                'doc': [
                    'https://github.com/Paymium/api-documentation',
                    'https://www.paymium.com/page/developers',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'countries',
                        'data/{id}/ticker',
                        'data/{id}/trades',
                        'data/{id}/depth',
                        'bitcoin_charts/{id}/trades',
                        'bitcoin_charts/{id}/depth',
                    ],
                },
                'private': {
                    'get': [
                        'merchant/get_payment/{UUID}',
                        'user',
                        'user/addresses',
                        'user/addresses/{btc_address}',
                        'user/orders',
                        'user/orders/{UUID}',
                        'user/price_alerts',
                    ],
                    'post': [
                        'user/orders',
                        'user/addresses',
                        'user/payment_requests',
                        'user/price_alerts',
                        'merchant/create_payment',
                    ],
                    'delete': [
                        'user/orders/{UUID}/cancel',
                        'user/price_alerts/{id}',
                    ],
                },
            },
            'markets': {
                'BTC/EUR': {'id': 'eur', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR'},
            },
            'fees': {
                'trading': {
                    'maker': 0.0059,
                    'taker': 0.0059,
                },
            },
        })

    async def fetch_balance(self, params={}):
        balances = await self.privateGetUser()
        result = {'info': balances}
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            lowercase = currency.lower()
            account = self.account()
            balance = 'balance_' + lowercase
            locked = 'locked_' + lowercase
            if balance in balances:
                account['free'] = balances[balance]
            if locked in balances:
                account['used'] = balances[locked]
            account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, params={}):
        orderbook = await self.publicGetDataIdDepth(self.extend({
            'id': self.market_id(symbol),
        }, params))
        result = self.parse_order_book(orderbook, None, 'bids', 'asks', 'price', 'amount')
        result['bids'] = self.sort_by(result['bids'], 0, True)
        return result

    async def fetch_ticker(self, symbol, params={}):
        ticker = await self.publicGetDataIdTicker(self.extend({
            'id': self.market_id(symbol),
        }, params))
        timestamp = ticker['at'] * 1000
        vwap = float(ticker['vwap'])
        baseVolume = float(ticker['volume'])
        quoteVolume = baseVolume * vwap
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'ask': float(ticker['ask']),
            'vwap': vwap,
            'open': float(ticker['open']),
            'close': None,
            'first': None,
            'last': float(ticker['price']),
            'change': None,
            'percentage': float(ticker['variation']),
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['created_at_int']) * 1000
        volume = 'traded_' + market['base'].lower()
        return {
            'info': trade,
            'id': trade['uuid'],
            'order': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': None,
            'side': trade['side'],
            'price': trade['price'],
            'amount': trade[volume],
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        response = await self.publicGetDataIdTrades(self.extend({
            'id': market['id'],
        }, params))
        return self.parse_trades(response, market)

    async def create_order(self, market, type, side, amount, price=None, params={}):
        order = {
            'type': self.capitalize(type) + 'Order',
            'currency': self.market_id(market),
            'direction': side,
            'amount': amount,
        }
        if type == 'market':
            order['price'] = price
        response = await self.privatePostUserOrders(self.extend(order, params))
        return {
            'info': response,
            'id': response['uuid'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        return await self.privatePostCancelOrder(self.extend({
            'orderNumber': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            body = self.json(params)
            nonce = str(self.nonce())
            auth = nonce + url + body
            headers = {
                'Api-Key': self.apiKey,
                'Api-Signature': self.hmac(self.encode(auth), self.secret),
                'Api-Nonce': nonce,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if 'errors' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
