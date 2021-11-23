# -*- coding: utf-8 -*-

"""CCXT: CryptoCurrency eXchange Trading Library (Async)"""

# -----------------------------------------------------------------------------

__version__ = '1.10.189'

# -----------------------------------------------------------------------------

from modified_ccxt.async.base.exchange import Exchange                   # noqa: F401

from modified_ccxt.base import errors                                    # noqa: F401
from modified_ccxt.base.errors import BaseError                          # noqa: F401
from modified_ccxt.base.errors import ExchangeError                      # noqa: F401
from modified_ccxt.base.errors import NotSupported                       # noqa: F401
from modified_ccxt.base.errors import AuthenticationError                # noqa: F401
from modified_ccxt.base.errors import InvalidNonce                       # noqa: F401
from modified_ccxt.base.errors import InsufficientFunds                  # noqa: F401
from modified_ccxt.base.errors import InvalidOrder                       # noqa: F401
from modified_ccxt.base.errors import OrderNotFound                      # noqa: F401
from modified_ccxt.base.errors import OrderNotCached                     # noqa: F401
from modified_ccxt.base.errors import CancelPending                      # noqa: F401
from modified_ccxt.base.errors import NetworkError                       # noqa: F401
from modified_ccxt.base.errors import DDoSProtection                     # noqa: F401
from modified_ccxt.base.errors import RequestTimeout                     # noqa: F401
from modified_ccxt.base.errors import ExchangeNotAvailable               # noqa: F401

from modified_ccxt.async._1broker import _1broker                        # noqa: F401
from modified_ccxt.async._1btcxe import _1btcxe                          # noqa: F401
from modified_ccxt.async.acx import acx                                  # noqa: F401
from modified_ccxt.async.allcoin import allcoin                          # noqa: F401
from modified_ccxt.async.anxpro import anxpro                            # noqa: F401
from modified_ccxt.async.binance import binance                          # noqa: F401
from modified_ccxt.async.bit2c import bit2c                              # noqa: F401
from modified_ccxt.async.bitbay import bitbay                            # noqa: F401
from modified_ccxt.async.bitcoincoid import bitcoincoid                  # noqa: F401
from modified_ccxt.async.bitfinex import bitfinex                        # noqa: F401
from modified_ccxt.async.bitfinex2 import bitfinex2                      # noqa: F401
from modified_ccxt.async.bitflyer import bitflyer                        # noqa: F401
from modified_ccxt.async.bithumb import bithumb                          # noqa: F401
from modified_ccxt.async.bitlish import bitlish                          # noqa: F401
from modified_ccxt.async.bitmarket import bitmarket                      # noqa: F401
from modified_ccxt.async.bitmex import bitmex                            # noqa: F401
from modified_ccxt.async.bitso import bitso                              # noqa: F401
from modified_ccxt.async.bitstamp import bitstamp                        # noqa: F401
from modified_ccxt.async.bitstamp1 import bitstamp1                      # noqa: F401
from modified_ccxt.async.bittrex import bittrex                          # noqa: F401
from modified_ccxt.async.bl3p import bl3p                                # noqa: F401
from modified_ccxt.async.bleutrade import bleutrade                      # noqa: F401
from modified_ccxt.async.btcbox import btcbox                            # noqa: F401
from modified_ccxt.async.btcchina import btcchina                        # noqa: F401
from modified_ccxt.async.btcexchange import btcexchange                  # noqa: F401
from modified_ccxt.async.btcmarkets import btcmarkets                    # noqa: F401
from modified_ccxt.async.btctradeua import btctradeua                    # noqa: F401
from modified_ccxt.async.btcturk import btcturk                          # noqa: F401
from modified_ccxt.async.btcx import btcx                                # noqa: F401
from modified_ccxt.async.bter import bter                                # noqa: F401
from modified_ccxt.async.bxinth import bxinth                            # noqa: F401
from modified_ccxt.async.ccex import ccex                                # noqa: F401
from modified_ccxt.async.cex import cex                                  # noqa: F401
from modified_ccxt.async.chbtc import chbtc                              # noqa: F401
from modified_ccxt.async.chilebit import chilebit                        # noqa: F401
from modified_ccxt.async.coincheck import coincheck                      # noqa: F401
from modified_ccxt.async.coinfloor import coinfloor                      # noqa: F401
from modified_ccxt.async.coingi import coingi                            # noqa: F401
from modified_ccxt.async.coinmarketcap import coinmarketcap              # noqa: F401
from modified_ccxt.async.coinmate import coinmate                        # noqa: F401
from modified_ccxt.async.coinsecure import coinsecure                    # noqa: F401
from modified_ccxt.async.coinspot import coinspot                        # noqa: F401
from modified_ccxt.async.cryptopia import cryptopia                      # noqa: F401
from modified_ccxt.async.dsx import dsx                                  # noqa: F401
from modified_ccxt.async.exmo import exmo                                # noqa: F401
from modified_ccxt.async.flowbtc import flowbtc                          # noqa: F401
from modified_ccxt.async.foxbit import foxbit                            # noqa: F401
from modified_ccxt.async.fybse import fybse                              # noqa: F401
from modified_ccxt.async.fybsg import fybsg                              # noqa: F401
from modified_ccxt.async.gatecoin import gatecoin                        # noqa: F401
from modified_ccxt.async.gateio import gateio                            # noqa: F401
from modified_ccxt.async.gdax import gdax                                # noqa: F401
from modified_ccxt.async.gemini import gemini                            # noqa: F401
from modified_ccxt.async.hitbtc import hitbtc                            # noqa: F401
from modified_ccxt.async.hitbtc2 import hitbtc2                          # noqa: F401
from modified_ccxt.async.huobi import huobi                              # noqa: F401
from modified_ccxt.async.huobicny import huobicny                        # noqa: F401
from modified_ccxt.async.huobipro import huobipro                        # noqa: F401
from modified_ccxt.async.independentreserve import independentreserve    # noqa: F401
from modified_ccxt.async.itbit import itbit                              # noqa: F401
from modified_ccxt.async.jubi import jubi                                # noqa: F401
from modified_ccxt.async.kraken import kraken                            # noqa: F401
from modified_ccxt.async.kuna import kuna                                # noqa: F401
from modified_ccxt.async.lakebtc import lakebtc                          # noqa: F401
from modified_ccxt.async.liqui import liqui                              # noqa: F401
from modified_ccxt.async.livecoin import livecoin                        # noqa: F401
from modified_ccxt.async.luno import luno                                # noqa: F401
from modified_ccxt.async.mercado import mercado                          # noqa: F401
from modified_ccxt.async.mixcoins import mixcoins                        # noqa: F401
from modified_ccxt.async.nova import nova                                # noqa: F401
from modified_ccxt.async.okcoincny import okcoincny                      # noqa: F401
from modified_ccxt.async.okcoinusd import okcoinusd                      # noqa: F401
from modified_ccxt.async.okex import okex                                # noqa: F401
from modified_ccxt.async.paymium import paymium                          # noqa: F401
from modified_ccxt.async.poloniex import poloniex                        # noqa: F401
from modified_ccxt.async.qryptos import qryptos                          # noqa: F401
from modified_ccxt.async.quadrigacx import quadrigacx                    # noqa: F401
from modified_ccxt.async.quoine import quoine                            # noqa: F401
from modified_ccxt.async.southxchange import southxchange                # noqa: F401
from modified_ccxt.async.surbitcoin import surbitcoin                    # noqa: F401
from modified_ccxt.async.therock import therock                          # noqa: F401
from modified_ccxt.async.tidex import tidex                              # noqa: F401
from modified_ccxt.async.urdubit import urdubit                          # noqa: F401
from modified_ccxt.async.vaultoro import vaultoro                        # noqa: F401
from modified_ccxt.async.vbtc import vbtc                                # noqa: F401
from modified_ccxt.async.virwox import virwox                            # noqa: F401
from modified_ccxt.async.wex import wex                                  # noqa: F401
from modified_ccxt.async.xbtce import xbtce                              # noqa: F401
from modified_ccxt.async.yobit import yobit                              # noqa: F401
from modified_ccxt.async.yunbi import yunbi                              # noqa: F401
from modified_ccxt.async.zaif import zaif                                # noqa: F401
from modified_ccxt.async.zb import zb                                    # noqa: F401

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
]

base = [
    'Exchange',
    'exchanges',
]

__all__ = base + errors.__all__ + exchanges
