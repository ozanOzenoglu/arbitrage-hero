# -*- coding: utf-8 -*-

from modified_ccxt.base.exchange import Exchange
import hashlib
from modified_ccxt.base.errors import ExchangeError


class nova (Exchange):

    def describe(self):
        return self.deep_extend(super(nova, self).describe(), {
            'id': 'nova',
            'name': 'Novaexchange',
            'countries': 'TZ',  # Tanzania
            'rateLimit': 2000,
            'version': 'v2',
            'hasCORS': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30518571-78ca0bca-9b8a-11e7-8840-64b83a4a94b2.jpg',
                'api': 'https://novaexchange.com/remote',
                'www': 'https://novaexchange.com',
                'doc': 'https://novaexchange.com/remote/faq',
            },
            'api': {
                'public': {
                    'get': [
                        'markets/',
                        'markets/{basecurrency}/',
                        'market/info/{pair}/',
                        'market/orderhistory/{pair}/',
                        'market/openorders/{pair}/buy/',
                        'market/openorders/{pair}/sell/',
                        'market/openorders/{pair}/both/',
                        'market/openorders/{pair}/{ordertype}/',
                    ],
                },
                'private': {
                    'post': [
                        'getbalances/',
                        'getbalance/{currency}/',
                        'getdeposits/',
                        'getwithdrawals/',
                        'getnewdepositaddress/{currency}/',
                        'getdepositaddress/{currency}/',
                        'myopenorders/',
                        'myopenorders_market/{pair}/',
                        'cancelorder/{orderid}/',
                        'withdraw/{currency}/',
                        'trade/{pair}/',
                        'tradehistory/',
                        'getdeposithistory/',
                        'getwithdrawalhistory/',
                        'walletstatus/',
                        'walletstatus/{currency}/',
                    ],
                },
            },
        })

    def fetch_markets(self):
        response = self.publicGetMarkets()
        markets = response['markets']
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            if not market['disabled']:
                id = market['marketname']
                quote, base = id.split('_')
                symbol = base + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'info': market,
                })
        return result

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        orderbook = self.publicGetMarketOpenordersPairBoth(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook, None, 'buyorders', 'sellorders', 'price', 'amount')

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        response = self.publicGetMarketInfoPair(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        ticker = response['markets'][0]
        timestamp = self.milliseconds()
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high24h']),
            'low': float(ticker['low24h']),
            'bid': self.safe_float(ticker, 'bid'),
            'ask': self.safe_float(ticker, 'ask'),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['last_price']),
            'change': float(ticker['change24h']),
            'percentage': None,
            'average': None,
            'baseVolume': None,
            'quoteVolume': float(ticker['volume24h']),
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = trade['unix_t_datestamp'] * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': None,
            'order': None,
            'type': None,
            'side': trade['tradetype'].lower(),
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetMarketOrderhistoryPair(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response['items'], market)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetbalances()
        balances = response['balances']
        result = {'info': response}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['currency']
            lockbox = float(balance['amount_lockbox'])
            trades = float(balance['amount_trades'])
            account = {
                'free': float(balance['amount']),
                'used': self.sum(lockbox, trades),
                'total': float(balance['amount_total']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        amount = str(amount)
        price = str(price)
        market = self.market(symbol)
        order = {
            'tradetype': side.upper(),
            'tradeamount': amount,
            'tradeprice': price,
            'tradebase': 1,
            'pair': market['id'],
        }
        response = self.privatePostTradePair(self.extend(order, params))
        return {
            'info': response,
            'id': None,
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelorder(self.extend({
            'orderid': id,
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/'
        if api == 'private':
            url += api + '/'
        url += self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            url += '?' + self.urlencode({'nonce': nonce})
            signature = self.hmac(self.encode(url), self.encode(self.secret), hashlib.sha512, 'base64')
            body = self.urlencode(self.extend({
                'apikey': self.apiKey,
                'signature': signature,
            }, query))
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] != 'success':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response
