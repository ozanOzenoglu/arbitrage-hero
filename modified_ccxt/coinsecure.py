# -*- coding: utf-8 -*-

from modified_ccxt.base.exchange import Exchange
from modified_ccxt.base.errors import ExchangeError


class coinsecure (Exchange):

    def describe(self):
        return self.deep_extend(super(coinsecure, self).describe(), {
            'id': 'coinsecure',
            'name': 'Coinsecure',
            'countries': 'IN',  # India
            'rateLimit': 1000,
            'version': 'v1',
            'hasCORS': True,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766472-9cbd200a-5ed9-11e7-9551-2267ad7bac08.jpg',
                'api': 'https://api.coinsecure.in',
                'www': 'https://coinsecure.in',
                'doc': [
                    'https://api.coinsecure.in',
                    'https://github.com/coinsecure/plugins',
                ],
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': False,
            },
            'api': {
                'public': {
                    'get': [
                        'bitcoin/search/confirmation/{txid}',
                        'exchange/ask/low',
                        'exchange/ask/orders',
                        'exchange/bid/high',
                        'exchange/bid/orders',
                        'exchange/lastTrade',
                        'exchange/max24Hr',
                        'exchange/min24Hr',
                        'exchange/ticker',
                        'exchange/trades',
                    ],
                },
                'private': {
                    'get': [
                        'mfa/authy/call',
                        'mfa/authy/sms',
                        'netki/search/{netkiName}',
                        'user/bank/otp/{number}',
                        'user/kyc/otp/{number}',
                        'user/profile/phone/otp/{number}',
                        'user/wallet/coin/address/{id}',
                        'user/wallet/coin/deposit/confirmed/all',
                        'user/wallet/coin/deposit/confirmed/{id}',
                        'user/wallet/coin/deposit/unconfirmed/all',
                        'user/wallet/coin/deposit/unconfirmed/{id}',
                        'user/wallet/coin/wallets',
                        'user/exchange/bank/fiat/accounts',
                        'user/exchange/bank/fiat/balance/available',
                        'user/exchange/bank/fiat/balance/pending',
                        'user/exchange/bank/fiat/balance/total',
                        'user/exchange/bank/fiat/deposit/cancelled',
                        'user/exchange/bank/fiat/deposit/unverified',
                        'user/exchange/bank/fiat/deposit/verified',
                        'user/exchange/bank/fiat/withdraw/cancelled',
                        'user/exchange/bank/fiat/withdraw/completed',
                        'user/exchange/bank/fiat/withdraw/unverified',
                        'user/exchange/bank/fiat/withdraw/verified',
                        'user/exchange/ask/cancelled',
                        'user/exchange/ask/completed',
                        'user/exchange/ask/pending',
                        'user/exchange/bid/cancelled',
                        'user/exchange/bid/completed',
                        'user/exchange/bid/pending',
                        'user/exchange/bank/coin/addresses',
                        'user/exchange/bank/coin/balance/available',
                        'user/exchange/bank/coin/balance/pending',
                        'user/exchange/bank/coin/balance/total',
                        'user/exchange/bank/coin/deposit/cancelled',
                        'user/exchange/bank/coin/deposit/unverified',
                        'user/exchange/bank/coin/deposit/verified',
                        'user/exchange/bank/coin/withdraw/cancelled',
                        'user/exchange/bank/coin/withdraw/completed',
                        'user/exchange/bank/coin/withdraw/unverified',
                        'user/exchange/bank/coin/withdraw/verified',
                        'user/exchange/bank/summary',
                        'user/exchange/coin/fee',
                        'user/exchange/fiat/fee',
                        'user/exchange/kycs',
                        'user/exchange/referral/coin/paid',
                        'user/exchange/referral/coin/successful',
                        'user/exchange/referral/fiat/paid',
                        'user/exchange/referrals',
                        'user/exchange/trade/summary',
                        'user/login/token/{token}',
                        'user/summary',
                        'user/wallet/summary',
                        'wallet/coin/withdraw/cancelled',
                        'wallet/coin/withdraw/completed',
                        'wallet/coin/withdraw/unverified',
                        'wallet/coin/withdraw/verified',
                    ],
                    'post': [
                        'login',
                        'login/initiate',
                        'login/password/forgot',
                        'mfa/authy/initiate',
                        'mfa/ga/initiate',
                        'signup',
                        'user/netki/update',
                        'user/profile/image/update',
                        'user/exchange/bank/coin/withdraw/initiate',
                        'user/exchange/bank/coin/withdraw/newVerifycode',
                        'user/exchange/bank/fiat/withdraw/initiate',
                        'user/exchange/bank/fiat/withdraw/newVerifycode',
                        'user/password/change',
                        'user/password/reset',
                        'user/wallet/coin/withdraw/initiate',
                        'wallet/coin/withdraw/newVerifycode',
                    ],
                    'put': [
                        'signup/verify/{token}',
                        'user/exchange/kyc',
                        'user/exchange/bank/fiat/deposit/new',
                        'user/exchange/ask/new',
                        'user/exchange/bid/new',
                        'user/exchange/instant/buy',
                        'user/exchange/instant/sell',
                        'user/exchange/bank/coin/withdraw/verify',
                        'user/exchange/bank/fiat/account/new',
                        'user/exchange/bank/fiat/withdraw/verify',
                        'user/mfa/authy/initiate/enable',
                        'user/mfa/ga/initiate/enable',
                        'user/netki/create',
                        'user/profile/phone/new',
                        'user/wallet/coin/address/new',
                        'user/wallet/coin/new',
                        'user/wallet/coin/withdraw/sendToExchange',
                        'user/wallet/coin/withdraw/verify',
                    ],
                    'delete': [
                        'user/gcm/{code}',
                        'user/logout',
                        'user/exchange/bank/coin/withdraw/unverified/cancel/{withdrawID}',
                        'user/exchange/bank/fiat/deposit/cancel/{depositID}',
                        'user/exchange/ask/cancel/{orderID}',
                        'user/exchange/bid/cancel/{orderID}',
                        'user/exchange/bank/fiat/withdraw/unverified/cancel/{withdrawID}',
                        'user/mfa/authy/disable/{code}',
                        'user/mfa/ga/disable/{code}',
                        'user/profile/phone/delete',
                        'user/profile/image/delete/{netkiName}',
                        'user/wallet/coin/withdraw/unverified/cancel/{withdrawID}',
                    ],
                },
            },
            'markets': {
                'BTC/INR': {'id': 'BTC/INR', 'symbol': 'BTC/INR', 'base': 'BTC', 'quote': 'INR'},
            },
            'fees': {
                'trading': {
                    'maker': 0.4 / 100,
                    'taker': 0.4 / 100,
                },
            },
        })

    def fetch_balance(self, params={}):
        response = self.privateGetUserExchangeBankSummary()
        balance = response['message']
        coin = {
            'free': balance['availableCoinBalance'],
            'used': balance['pendingCoinBalance'],
            'total': balance['totalCoinBalance'],
        }
        fiat = {
            'free': balance['availableFiatBalance'],
            'used': balance['pendingFiatBalance'],
            'total': balance['totalFiatBalance'],
        }
        result = {
            'info': balance,
            'BTC': coin,
            'INR': fiat,
        }
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, params={}):
        bids = self.publicGetExchangeBidOrders(params)
        asks = self.publicGetExchangeAskOrders(params)
        orderbook = {
            'bids': bids['message'],
            'asks': asks['message'],
        }
        return self.parse_order_book(orderbook, None, 'bids', 'asks', 'rate', 'vol')

    def fetch_ticker(self, symbol, params={}):
        response = self.publicGetExchangeTicker(params)
        ticker = response['message']
        timestamp = ticker['timestamp']
        baseVolume = float(ticker['coinvolume'])
        if symbol == 'BTC/INR':
            satoshi = 0.00000001
            baseVolume = baseVolume * satoshi
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
            'last': float(ticker['lastPrice']),
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': float(ticker['fiatvolume']),
            'info': ticker,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        return self.publicGetExchangeTrades(params)

    def create_order(self, market, type, side, amount, price=None, params={}):
        method = 'privatePutUserExchange'
        order = {}
        if type == 'market':
            method += 'Instant' + self.capitalize(side)
            if side == 'buy':
                order['maxFiat'] = amount
            else:
                order['maxVol'] = amount
        else:
            direction = 'Bid' if (side == 'buy') else 'Ask'
            method += direction + 'New'
            order['rate'] = price
            order['vol'] = amount
        response = getattr(self, method)(self.extend(order, params))
        return {
            'info': response,
            'id': response['message']['orderID'],
        }

    def cancel_order(self, id, symbol=None, params={}):
        raise ExchangeError(self.id + ' cancelOrder() is not fully implemented yet')
        method = 'privateDeleteUserExchangeAskCancelOrderId'  # TODO fixme, have to specify order side here
        return getattr(self, method)({'orderID': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            self.check_required_credentials()
            headers = {'Authorization': self.apiKey}
            if query:
                body = self.json(query)
                headers['Content-Type'] = 'application/json'
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if 'success' in response:
            if response['success']:
                return response
        raise ExchangeError(self.id + ' ' + self.json(response))
