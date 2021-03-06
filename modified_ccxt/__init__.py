# -*- coding: utf-8 -*-

"""CCXT: CryptoCurrency eXchange Trading Library"""

"""
MIT License

Copyright (c) 2017 Igor Kroitor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ----------------------------------------------------------------------------

__version__ = '1.10.189'

# ----------------------------------------------------------------------------

from modified_ccxt.base.exchange import Exchange                     # noqa: F401

from modified_ccxt.base import errors                                # noqa: F401
from modified_ccxt.base.errors import BaseError                      # noqa: F401
from modified_ccxt.base.errors import ExchangeError                  # noqa: F401
from modified_ccxt.base.errors import NotSupported                   # noqa: F401
from modified_ccxt.base.errors import AuthenticationError            # noqa: F401
from modified_ccxt.base.errors import InvalidNonce                   # noqa: F401
from modified_ccxt.base.errors import InsufficientFunds              # noqa: F401
from modified_ccxt.base.errors import InvalidOrder                   # noqa: F401
from modified_ccxt.base.errors import OrderNotFound                  # noqa: F401
from modified_ccxt.base.errors import OrderNotCached                 # noqa: F401
from modified_ccxt.base.errors import CancelPending                  # noqa: F401
from modified_ccxt.base.errors import NetworkError                   # noqa: F401
from modified_ccxt.base.errors import DDoSProtection                 # noqa: F401
from modified_ccxt.base.errors import RequestTimeout                 # noqa: F401
from modified_ccxt.base.errors import ExchangeNotAvailable           # noqa: F401

from modified_ccxt._1broker import _1broker                          # noqa: F401
from modified_ccxt._1btcxe import _1btcxe                            # noqa: F401
from modified_ccxt.acx import acx                                    # noqa: F401
from modified_ccxt.allcoin import allcoin                            # noqa: F401
from modified_ccxt.anxpro import anxpro                              # noqa: F401
from modified_ccxt.binance import binance                            # noqa: F401
from modified_ccxt.bit2c import bit2c                                # noqa: F401
from modified_ccxt.bitbay import bitbay                              # noqa: F401
from modified_ccxt.bitcoincoid import bitcoincoid                    # noqa: F401
from modified_ccxt.bitfinex import bitfinex                          # noqa: F401
from modified_ccxt.bitfinex2 import bitfinex2                        # noqa: F401
from modified_ccxt.bitflyer import bitflyer                          # noqa: F401
from modified_ccxt.bithumb import bithumb                            # noqa: F401
from modified_ccxt.bitlish import bitlish                            # noqa: F401
from modified_ccxt.bitmarket import bitmarket                        # noqa: F401
from modified_ccxt.bitmex import bitmex                              # noqa: F401
from modified_ccxt.bitso import bitso                                # noqa: F401
from modified_ccxt.bitstamp import bitstamp                          # noqa: F401
from modified_ccxt.bitstamp1 import bitstamp1                        # noqa: F401
from modified_ccxt.bittrex import bittrex                            # noqa: F401
from modified_ccxt.bl3p import bl3p                                  # noqa: F401
from modified_ccxt.bleutrade import bleutrade                        # noqa: F401
from modified_ccxt.btcbox import btcbox                              # noqa: F401
from modified_ccxt.btcchina import btcchina                          # noqa: F401
from modified_ccxt.btcexchange import btcexchange                    # noqa: F401
from modified_ccxt.btcmarkets import btcmarkets                      # noqa: F401
from modified_ccxt.btctradeua import btctradeua                      # noqa: F401
from modified_ccxt.btcturk import btcturk                            # noqa: F401
from modified_ccxt.btcx import btcx                                  # noqa: F401
from modified_ccxt.bter import bter                                  # noqa: F401
from modified_ccxt.bxinth import bxinth                              # noqa: F401
from modified_ccxt.ccex import ccex                                  # noqa: F401
from modified_ccxt.cex import cex                                    # noqa: F401
from modified_ccxt.chbtc import chbtc                                # noqa: F401
from modified_ccxt.chilebit import chilebit                          # noqa: F401
from modified_ccxt.coincheck import coincheck                        # noqa: F401
from modified_ccxt.coinfloor import coinfloor                        # noqa: F401
from modified_ccxt.coingi import coingi                              # noqa: F401
from modified_ccxt.coinmarketcap import coinmarketcap                # noqa: F401
from modified_ccxt.coinmate import coinmate                          # noqa: F401
from modified_ccxt.coinsecure import coinsecure                      # noqa: F401
from modified_ccxt.coinspot import coinspot                          # noqa: F401
from modified_ccxt.cryptopia import cryptopia                        # noqa: F401
from modified_ccxt.dsx import dsx                                    # noqa: F401
from modified_ccxt.exmo import exmo                                  # noqa: F401
from modified_ccxt.flowbtc import flowbtc                            # noqa: F401
from modified_ccxt.foxbit import foxbit                              # noqa: F401
from modified_ccxt.fybse import fybse                                # noqa: F401
from modified_ccxt.fybsg import fybsg                                # noqa: F401
from modified_ccxt.gatecoin import gatecoin                          # noqa: F401
from modified_ccxt.gateio import gateio                              # noqa: F401
from modified_ccxt.gdax import gdax                                  # noqa: F401
from modified_ccxt.gemini import gemini                              # noqa: F401
from modified_ccxt.hitbtc import hitbtc                              # noqa: F401
from modified_ccxt.hitbtc2 import hitbtc2                            # noqa: F401
from modified_ccxt.huobi import huobi                                # noqa: F401
from modified_ccxt.huobicny import huobicny                          # noqa: F401
from modified_ccxt.huobipro import huobipro                          # noqa: F401
from modified_ccxt.independentreserve import independentreserve      # noqa: F401
from modified_ccxt.itbit import itbit                                # noqa: F401
from modified_ccxt.jubi import jubi                                  # noqa: F401
from modified_ccxt.kraken import kraken                              # noqa: F401
from modified_ccxt.kuna import kuna                                  # noqa: F401
from modified_ccxt.lakebtc import lakebtc                            # noqa: F401
from modified_ccxt.liqui import liqui                                # noqa: F401
from modified_ccxt.livecoin import livecoin                          # noqa: F401
from modified_ccxt.luno import luno                                  # noqa: F401
from modified_ccxt.mercado import mercado                            # noqa: F401
from modified_ccxt.mixcoins import mixcoins                          # noqa: F401
from modified_ccxt.nova import nova                                  # noqa: F401
from modified_ccxt.okcoincny import okcoincny                        # noqa: F401
from modified_ccxt.okcoinusd import okcoinusd                        # noqa: F401
from modified_ccxt.okex import okex                                  # noqa: F401
from modified_ccxt.paymium import paymium                            # noqa: F401
from modified_ccxt.poloniex import poloniex                          # noqa: F401
from modified_ccxt.qryptos import qryptos                            # noqa: F401
from modified_ccxt.quadrigacx import quadrigacx                      # noqa: F401
from modified_ccxt.quoine import quoine                              # noqa: F401
from modified_ccxt.southxchange import southxchange                  # noqa: F401
from modified_ccxt.surbitcoin import surbitcoin                      # noqa: F401
from modified_ccxt.therock import therock                            # noqa: F401
from modified_ccxt.tidex import tidex                                # noqa: F401
from modified_ccxt.urdubit import urdubit                            # noqa: F401
from modified_ccxt.vaultoro import vaultoro                          # noqa: F401
from modified_ccxt.vbtc import vbtc                                  # noqa: F401
from modified_ccxt.virwox import virwox                              # noqa: F401
from modified_ccxt.wex import wex                                    # noqa: F401
from modified_ccxt.xbtce import xbtce                                # noqa: F401
from modified_ccxt.yobit import yobit                                # noqa: F401
from modified_ccxt.yunbi import yunbi                                # noqa: F401
from modified_ccxt.zaif import zaif                                  # noqa: F401
from modified_ccxt.zb import zb                                      # noqa: F401
from modified_ccxt.koineks import koineks
from modified_ccxt.vebit import vebit
from modified_ccxt.koinim import koinim
exchanges = [
    '_1broker',
    '_1btcxe',
    'acx',
    'allcoin',
    'anxpro',
    'binance',
    'bit2c',
    'bitbay',
    'bitcoincoid',
    'bitfinex',
    'bitfinex2',
    'bitflyer',
    'bithumb',
    'bitlish',
    'bitmarket',
    'bitmex',
    'bitso',
    'bitstamp',
    'bitstamp1',
    'bittrex',
    'bl3p',
    'bleutrade',
    'btcbox',
    'btcchina',
    'btcexchange',
    'btcmarkets',
    'btctradeua',
    'btcturk',
    'btcx',
    'bter',
    'bxinth',
    'ccex',
    'cex',
    'chbtc',
    'chilebit',
    'coincheck',
    'coinfloor',
    'coingi',
    'coinmarketcap',
    'coinmate',
    'coinsecure',
    'coinspot',
    'cryptopia',
    'dsx',
    'exmo',
    'flowbtc',
    'foxbit',
    'fybse',
    'fybsg',
    'gatecoin',
    'gateio',
    'gdax',
    'gemini',
    'hitbtc',
    'hitbtc2',
    'huobi',
    'huobicny',
    'huobipro',
    'independentreserve',
    'itbit',
    'jubi',
    'kraken',
    'kuna',
    'lakebtc',
    'liqui',
    'livecoin',
    'luno',
    'mercado',
    'mixcoins',
    'nova',
    'okcoincny',
    'okcoinusd',
    'okex',
    'paymium',
    'poloniex',
    'qryptos',
    'quadrigacx',
    'quoine',
    'southxchange',
    'surbitcoin',
    'therock',
    'tidex',
    'urdubit',
    'vaultoro',
    'vbtc',
    'virwox',
    'wex',
    'xbtce',
    'yobit',
    'yunbi',
    'zaif',
    'zb',
    'koineks',
    'vebit',
    'koinim',
]

base = [
    'Exchange',
    'exchanges',
]

__all__ = base + errors.__all__ + exchanges
