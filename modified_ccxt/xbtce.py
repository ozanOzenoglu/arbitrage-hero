# -*- coding: utf-8 -*-

from modified_ccxt.base.exchange import Exchange
import hashlib
from modified_ccxt.base.errors import ExchangeError
from modified_ccxt.base.errors import NotSupported
from modified_ccxt.base.errors import AuthenticationError


class xbtce (Exchange):

    def describe(self):
        return self.deep_extend(super(xbtce, self).describe(), {
            'id': 'xbtce',
            'name': 'xBTCe',
            'countries': 'RU',
            'rateLimit': 2000,  # responses are cached every 2 seconds
            'version': 'v1',
            'hasPublicAPI': False,
            'hasCORS': False,
            'hasFetchTickers': True,
            'hasFetchOHLCV': False,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/28059414-e235970c-662c-11e7-8c3a-08e31f78684b.jpg',
                'api': 'https://cryptottlivewebapi.xbtce.net:8443/api',
                'www': 'https://www.xbtce.com',
                'doc': [
                    'https://www.xbtce.com/tradeapi',
                    'https://support.xbtce.info/Knowledgebase/Article/View/52/25/xbtce-exchange-api',
                ],
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'uid': True,
            },
            'api': {
                'public': {
                    'get': [
                        'currency',
                        'currency/{filter}',
                        'level2',
                        'level2/{filter}',
                        'quotehistory/{symbol}/{periodicity}/bars/ask',
                        'quotehistory/{symbol}/{periodicity}/bars/bid',
                        'quotehistory/{symbol}/level2',
                        'quotehistory/{symbol}/ticks',
                        'symbol',
                        'symbol/{filter}',
                        'tick',
                        'tick/{filter}',
                        'ticker',
                        'ticker/{filter}',
                        'tradesession',
                    ],
                },
                'private': {
                    'get': [
                        'tradeserverinfo',
                        'tradesession',
                        'currency',
                        'currency/{filter}',
                        'level2',
                        'level2/{filter}',
                        'symbol',
                        'symbol/{filter}',
                        'tick',
                        'tick/{filter}',
                        'account',
                        'asset',
                        'asset/{id}',
                        'position',
                        'position/{id}',
                        'trade',
                        'trade/{id}',
                        'quotehistory/{symbol}/{periodicity}/bars/ask',
                        'quotehistory/{symbol}/{periodicity}/bars/ask/info',
                        'quotehistory/{symbol}/{periodicity}/bars/bid',
                        'quotehistory/{symbol}/{periodicity}/bars/bid/info',
                        'quotehistory/{symbol}/level2',
                        'quotehistory/{symbol}/level2/info',
                        'quotehistory/{symbol}/periodicities',
                        'quotehistory/{symbol}/ticks',
                        'quotehistory/{symbol}/ticks/info',
                        'quotehistory/cache/{symbol}/{periodicity}/bars/ask',
                        'quotehistory/cache/{symbol}/{periodicity}/bars/bid',
                        'quotehistory/cache/{symbol}/level2',
                        'quotehistory/cache/{symbol}/ticks',
                        'quotehistory/symbols',
                        'quotehistory/version',
                    ],
                    'post': [
                        'trade',
                        'tradehistory',
                    ],
                    'put': [
                        'trade',
                    ],
                    'delete': [
                        'trade',
                    ],
                },
            },
        })

    def fetch_markets(self):
        markets = self.privateGetSymbol()
        result = []
        for p in range(0, len(markets)):
            market = markets[p]
            id = market['Symbol']
            base = market['MarginCurrency']
            quote = market['ProfitCurrency']
            if base == 'DSH':
                base = 'DASH'
            symbol = base + '/' + quote
            symbol = symbol if market['IsTradeAllowed'] else id
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetAsset()
        result = {'info': balances}
        for b in range(0, len(balances)):
            balance = balances[b]
            currency = balance['Currency']
            uppercase = currency.upper()
            # xbtce names DASH incorrectly as DSH
            if uppercase == 'DSH':
                uppercase = 'DASH'
            account = {
                'free': balance['FreeAmount'],
                'used': balance['LockedAmount'],
                'total': balance['Amount'],
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.privateGetLevel2Filter(self.extend({
            'filter': market['id'],
        }, params))
        orderbook = orderbook[0]
        timestamp = orderbook['Timestamp']
        return self.parse_order_book(orderbook, timestamp, 'Bids', 'Asks', 'Price', 'Volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = 0
        last = None
        if 'LastBuyTimestamp' in ticker:
            if timestamp < ticker['LastBuyTimestamp']:
                timestamp = ticker['LastBuyTimestamp']
                last = ticker['LastBuyPrice']
        if 'LastSellTimestamp' in ticker:
            if timestamp < ticker['LastSellTimestamp']:
                timestamp = ticker['LastSellTimestamp']
                last = ticker['LastSellPrice']
        if not timestamp:
            timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': ticker['DailyBestBuyPrice'],
            'low': ticker['DailyBestSellPrice'],
            'bid': ticker['BestBid'],
            'ask': ticker['BestAsk'],
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': last,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': ticker['DailyTradedTotalVolume'],
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTicker(params)
        tickers = self.index_by(tickers, 'Symbol')
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = None
            symbol = None
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            else:
                base = id[0:3]
                quote = id[3:6]
                if base == 'DSH':
                    base = 'DASH'
                if quote == 'DSH':
                    quote = 'DASH'
                symbol = base + '/' + quote
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        tickers = self.publicGetTickerFilter(self.extend({
            'filter': market['id'],
        }, params))
        length = len(tickers)
        if length < 1:
            raise ExchangeError(self.id + ' fetchTicker returned empty response, xBTCe public API error')
        tickers = self.index_by(tickers, 'Symbol')
        ticker = tickers[market['id']]
        return self.parse_ticker(ticker, market)

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        # no method for trades?
        return self.privateGetTrade(params)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            ohlcv['Timestamp'],
            ohlcv['Open'],
            ohlcv['High'],
            ohlcv['Low'],
            ohlcv['Close'],
            ohlcv['Volume'],
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        raise NotSupported(self.id + ' fetchOHLCV is disabled by the exchange')
        minutes = int(timeframe / 60)  # 1 minute by default
        periodicity = str(minutes)
        self.load_markets()
        market = self.market(symbol)
        if not since:
            since = self.seconds() - 86400 * 7  # last day by defulat
        if not limit:
            limit = 1000  # default
        response = self.privateGetQuotehistorySymbolPeriodicityBarsBid(self.extend({
            'symbol': market['id'],
            'periodicity': periodicity,
            'timestamp': since,
            'count': limit,
        }, params))
        return self.parse_ohlcvs(response['Bars'], market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        response = self.tapiPostTrade(self.extend({
            'pair': self.market_id(symbol),
            'type': side,
            'amount': amount,
            'rate': price,
        }, params))
        return {
            'info': response,
            'id': str(response['Id']),
        }

    def cancel_order(self, id, symbol=None, params={}):
        return self.privateDeleteTrade(self.extend({
            'Type': 'Cancel',
            'Id': id,
        }, params))

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        if not self.apiKey:
            raise AuthenticationError(self.id + ' requires apiKey for all requests, their public API is always busy')
        if not self.uid:
            raise AuthenticationError(self.id + ' requires uid property for authentication and trading, their public API is always busy')
        url = self.urls['api'] + '/' + self.version
        if api == 'public':
            url += '/' + api
        url += '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            headers = {'Accept-Encoding': 'gzip, deflate'}
            nonce = str(self.nonce())
            if method == 'POST':
                if query:
                    headers['Content-Type'] = 'application/json'
                    body = self.json(query)
                else:
                    url += '?' + self.urlencode(query)
            auth = nonce + self.uid + self.apiKey + method + url
            if body:
                auth += body
            signature = self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha256, 'base64')
            credentials = self.uid + ':' + self.apiKey + ':' + nonce + ':' + self.binary_to_string(signature)
            headers['Authorization'] = 'HMAC ' + credentials
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
