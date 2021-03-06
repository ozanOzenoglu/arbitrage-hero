# -*- coding: utf-8 -*-

from modified_ccxt.async.base.exchange import Exchange
from modified_ccxt.base.errors import NotSupported


class bitlish (Exchange):

    def describe(self):
        return self.deep_extend(super(bitlish, self).describe(), {
            'id': 'bitlish',
            'name': 'bitlish',
            'countries': ['GB', 'EU', 'RU'],
            'rateLimit': 1500,
            'version': 'v1',
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': True,
            'hasWithdraw': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766275-dcfc6c30-5ed3-11e7-839d-00a846385d0b.jpg',
                'api': 'https://bitlish.com/api',
                'www': 'https://bitlish.com',
                'doc': 'https://bitlish.com/api',
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': False,
            },
            'api': {
                'public': {
                    'get': [
                        'instruments',
                        'ohlcv',
                        'pairs',
                        'tickers',
                        'trades_depth',
                        'trades_history',
                    ],
                    'post': [
                        'instruments',
                        'ohlcv',
                        'pairs',
                        'tickers',
                        'trades_depth',
                        'trades_history',
                    ],
                },
                'private': {
                    'post': [
                        'accounts_operations',
                        'balance',
                        'cancel_trade',
                        'cancel_trades_by_ids',
                        'cancel_all_trades',
                        'create_bcode',
                        'create_template_wallet',
                        'create_trade',
                        'deposit',
                        'list_accounts_operations_from_ts',
                        'list_active_trades',
                        'list_bcodes',
                        'list_my_matches_from_ts',
                        'list_my_trades',
                        'list_my_trads_from_ts',
                        'list_payment_methods',
                        'list_payments',
                        'redeem_code',
                        'resign',
                        'signin',
                        'signout',
                        'trade_details',
                        'trade_options',
                        'withdraw',
                        'withdraw_by_id',
                    ],
                },
            },
        })

    def common_currency_code(self, currency):
        if not self.substituteCommonCurrencyCodes:
            return currency
        if currency == 'XBT':
            return 'BTC'
        if currency == 'BCC':
            return 'BCH'
        if currency == 'DRK':
            return 'DASH'
        if currency == 'DSH':
            currency = 'DASH'
        return currency

    async def fetch_markets(self):
        markets = await self.publicGetPairs()
        result = []
        keys = list(markets.keys())
        for p in range(0, len(keys)):
            market = markets[keys[p]]
            id = market['id']
            symbol = market['name']
            base, quote = symbol.split('/')
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'high': self.safe_float(ticker, 'max'),
            'low': self.safe_float(ticker, 'min'),
            'bid': None,
            'ask': None,
            'vwap': None,
            'open': None,
            'close': None,
            'first': self.safe_float(ticker, 'first'),
            'last': self.safe_float(ticker, 'last'),
            'change': None,
            'percentage': self.safe_float(ticker, 'prc'),
            'average': None,
            'baseVolume': self.safe_float(ticker, 'sum'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        tickers = await self.publicGetTickers(params)
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
        tickers = await self.publicGetTickers(params)
        ticker = tickers[market['id']]
        return self.parse_ticker(ticker, market)

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        await self.load_markets()
        # market = self.market(symbol)
        now = self.seconds()
        start = now - 86400 * 30  # last 30 days
        interval = [str(start), None]
        return await self.publicPostOhlcv(self.extend({
            'time_range': interval,
        }, params))

    async def fetch_order_book(self, symbol, params={}):
        await self.load_markets()
        orderbook = await self.publicGetTradesDepth(self.extend({
            'pair_id': self.market_id(symbol),
        }, params))
        timestamp = int(int(orderbook['last']) / 1000)
        return self.parse_order_book(orderbook, timestamp, 'bid', 'ask', 'price', 'volume')

    def parse_trade(self, trade, market=None):
        side = 'buy' if (trade['dir'] == 'bid') else 'sell'
        symbol = None
        if market:
            symbol = market['symbol']
        timestamp = int(trade['created'] / 1000)
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetTradesHistory(self.extend({
            'pair_id': market['id'],
        }, params))
        return self.parse_trades(response['list'], market)

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostBalance()
        result = {'info': response}
        currencies = list(response.keys())
        balance = {}
        for c in range(0, len(currencies)):
            currency = currencies[c]
            account = response[currency]
            currency = currency.upper()
            # issue  #4 bitlish names Dash as DSH, instead of DASH
            if currency == 'DSH':
                currency = 'DASH'
            balance[currency] = account
        for c in range(0, len(self.currencies)):
            currency = self.currencies[c]
            account = self.account()
            if currency in balance:
                account['free'] = float(balance[currency]['funds'])
                account['used'] = float(balance[currency]['holded'])
                account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def sign_in(self):
        return self.privatePostSignin({
            'login': self.login,
            'passwd': self.password,
        })

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        order = {
            'pair_id': self.market_id(symbol),
            'dir': 'bid' if (side == 'buy') else 'ask',
            'amount': amount,
        }
        if type == 'limit':
            order['price'] = price
        result = await self.privatePostCreateTrade(self.extend(order, params))
        return {
            'info': result,
            'id': result['id'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        return await self.privatePostCancelTrade({'id': id})

    async def withdraw(self, currency, amount, address, params={}):
        await self.load_markets()
        if currency != 'BTC':
            # they did not document other types...
            raise NotSupported(self.id + ' currently supports BTC withdrawals only, until they document other currencies...')
        response = await self.privatePostWithdraw(self.extend({
            'currency': currency.lower(),
            'amount': float(amount),
            'account': address,
            'payment_method': 'bitcoin',  # they did not document other types...
        }, params))
        return {
            'info': response,
            'id': response['message_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if method == 'GET':
                if params:
                    url += '?' + self.urlencode(params)
            else:
                body = self.json(params)
                headers = {'Content-Type': 'application/json'}
        else:
            self.check_required_credentials()
            body = self.json(self.extend({'token': self.apiKey}, params))
            headers = {'Content-Type': 'application/json'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
