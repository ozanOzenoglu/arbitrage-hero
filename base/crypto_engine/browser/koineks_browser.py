import time
import requests
import json


from api.base.crypto_engine.browser.browser import MainBrowser
from api.base.crypto_engine.utils.mail import KoineksMail
from api.base.crypto_engine.browser.browser import LoginErrors


from base.crypto_engine.utils import helper
from base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine import symbols

def finder(method):
    def findit(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
            if result == None or len(result) == 0:
                return None
        except Exception as e:
            error("Finder Error: {:s} -> {:s}".format(str(e)))

        return result

    return findit


def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__),str(e)))

        return result

    return catched


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()

        result = method(*args, **kw)

        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            user_feedback('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed



class KoineksBrowser(MainBrowser):
    if (symbols.GET_SMS_FROM_SERVER_ENABLED):
        user_feedback("get sms from server is enabled")
        FIRST_SMS_CODE_WAIT_TIME = 5  # this is the first amount of time we will wait before trying to fetch sms_code
    else:
        FIRST_SMS_CODE_WAIT_TIME = 10
    LOGIN_URL = "https://koineks.com/login"
    TRY_AGAIN_WAIT_TIME = 50
    URL = "https://koineks.com"
    SMS_ACTIVATON_URL = "https://koineks.com/login-sms-activation"
    WALLET_URL = "https://koineks.com/wallet"

    def __init__(self, username: str, password: str,driver_name="firefox",headless=True):
        self.__mail_service = KoineksMail(username,password)
        super().__init__(username,password,driver_name,headless)

    @finder
    def _find_email_element(self):
        return self._browser.find_by_name("email")

    @finder
    def _find_password_element(self):
        return self._browser.find_by_name("password")

    # don't use finder for this function if you don't want to have nice exceptions :)
    def _find_login_button(self):
        button = self._browser.find_by_text('Giriş Yap')[1]
        if button._get_value() == 'Giriş Yap':
            return button
        else:
            return None

    @finder
    def _find_sms_item(self):
        return self._browser.find_by_id("sms-code")

    @finder
    def _find_sms_send_button(self):
        return self._browser.find_by_css('div button')

    def _find_reset_button(self):
        btn = self._browser.find_by_id('sms-reset')
        try:
            val = btn[0]._get_value()
            if (val != "Tekrar Gönder"):
                return None
            else:
                return btn
        except Exception as e:
            error("_find_reset_btn error {:s}".format(str(e)))
            return None

    def _is_first_try(self):
        try:
            first_try = self._browser.find_by_css('table')[0]._get_value().__contains__("Kalan Süre") != True
        except Exception as e:
            try_again = self._find_try_again_button()
            first_try = (try_again == None) or len(try_again) == 0
        return first_try

    def try_click_login(self, button):
        button_click_work = False
        try_count = 0
        while button_click_work == False:
            try:
                last_sms_time = int(self.get_last_sms_time())
                wait = 70 - last_sms_time
                if (wait > 0):
                    error("Last sms time is too new , wait {:d}".format(int(wait)))
                    time.sleep(wait)
                try_count += 1
                button.click()
                if (self.get_driver_name() == "firefox"):
                    button.click()
            except Exception as e:
                error("error button_click_work {:s}".format(str(e)))
            try:
                time.sleep(1)
                sms_verification_item = self._find_sms_item()
                if (sms_verification_item == None):
                    raise Exception()
                sms_verification_item._set_value("Sms Fetching.. Wait!")
                button_click_work = True
            except Exception as e:
                error_code = self.find_error()
                if error_code == LoginErrors.TRY_AGAIN:
                    return error_code
                error("Error finding sms verification item  due to Giriş Yap Button not clicked properly!")
                button_click_work = False
                if (try_count > 5):
                    raise e

        return button_click_work

    # TODO: get sms code from server..

    def get_last_sms_time(self):
        private_key = symbols.API_PRIVATE_KEY
        data = {'event': 'get_sms_code', 'data': 'null', 'private_key': private_key}
        r = requests.get("http://ozenoglu.com:8000/api_call", data=json.dumps(data))
        response = r.content.decode("utf-8").replace("\"", "")

        try_count = 0
        while True:
            try:
                try_count += 1
                update_time = response.split("update_time:")[1]
                update_time = float(update_time) / 1000
                now = time.time()
                return now - update_time
            except Exception as e:
                if (try_count > 5):
                    raise Exception("Error parsing update_time from server(sms_code) {:s}".format(str(e)))
                time.sleep(1)


    def get_sms_from_mail(self):
        return self.__mail_service.get_sms_verification_code()


    @trycatch
    def enter_sms_code(self):
        if (symbols.GET_SMS_FROM_SERVER_ENABLED):
            sms_code = helper.get_sms_code_from_server("koineks_login")
            if sms_code == None:
                user_feedback("sms_code is none try fetch from mail.")
                sms_code = self.get_sms_from_mail()
        else:
            sms_code = self.get_sms_from_mail()
        if sms_code == None:
            raise Exception("Sms can't fetched!")
        sms_verification_item = self._find_sms_item()
        if (sms_verification_item == None):
            raise Exception("Couldn't found sms_verification_item!")
        sms_verification_item._set_value(sms_code)
        send_button = self._find_sms_send_button()
        if (send_button == None):
            raise Exception("Sms Send button couldn't found")
        send_button.click()
        return True


    @finder
    def _find_try_again_button(self):
        return self._browser.find_by_text("Tekrar Dene")


    def find_error(self):
        try:
            try_again = self._find_try_again_button()
            if try_again != None:
                return LoginErrors.TRY_AGAIN
            elif self._driver.current_url != KoineksBrowser.SMS_ACTIVATON_URL:
                return LoginErrors.RE_LOGIN
            else:
                error("Could not find error root.")
                return None
        except Exception as e:
            error("Error during investigation on error code!")


    def _is_login_succeed(self):
        try:
            sms_result = self._browser.find_by_id('sms-messagebox')[0]._get_value()
            while (sms_result == "Yükleniyor..."):
                sms_result = self._browser.find_by_id('sms-messagebox')[0]._get_value()
                debug("SMS RESULT : {:s}".format(str(sms_result)))
                time.sleep(1)  # don't make cpu overloaded plz.

            user_feedback("FINAL SMS RESULT : {:s}".format(str(sms_result)))
            error_code = LoginErrors.NEED_TO_WAIT if "Tüm deneme haklarınız tükendi, lütfen bekleme süresi tamamlandıktan sonra tekrar deneyiniz." == sms_result else None
            error_code = LoginErrors.WRONG_SMS_CODE if "Güvenlik kodu doğrulanamadı." == sms_result else None
            if (error_code == None):
                return [True, None]
            return [False, error_code]
        except Exception as e:
            if self._browser.find_by_id('page-top') is not None:
                return [True, None]
            else:
                return [False, LoginErrors.WEIRD_CONDITION]  # Weird condition , should be investigated.

    def _find_remaining_time(self):
        try:
            sms_time_out_element = self._browser.find_by_id("sms-timeout")
            if sms_time_out_element != None:
                return int(sms_time_out_element._get_value())
            else:
                return KoineksBrowser.TRY_AGAIN_WAIT_TIME
        except Exception as e:
            error("Error _find_remaining_time {:s}".format(str(e)))


    def login(self):
        login_sucess = False
        wtf_count = 0
        while login_sucess == False:
            try:
                user_feedback("login process is started")
                if (self._is_first_try()):
                    self._browser.visit(KoineksBrowser.LOGIN_URL)
                    email_element = self._find_email_element()
                    password_element = self._find_password_element()
                    login_btn = self._find_login_button()

                    if email_element != None and password_element != None and login_btn != None:
                        email_element._set_value(self.get_user())
                        password_element._set_value(self.get_pass())
                        ret = self.try_click_login(login_btn)
                        time.sleep(2)
                        user_feedback("login button clicked")
                        while (ret == LoginErrors.TRY_AGAIN):
                            error("Try again error code , we will click that btn after 5 sec")
                            time.sleep(5)  # wait 5 sec and try later
                            try_again_btn = self._find_try_again_button()
                            if try_again_btn != None:
                                try_again_btn.click()
                            else:
                                error("We couldn't find try again button , go and login again!")
                                continue
                            ret = self.find_error()
                    else:
                        raise Exception("email , password , login elements can't find. (one of them at least)")
                else:
                    user_feedback("it is not first try!")
                    sms_reset_btn = self._find_reset_button()
                    if (sms_reset_btn != None):
                        sms_reset_btn.click()
                    else:
                        sms_txtbox = self._find_sms_item()
                        if (sms_txtbox != None):  # if we're here , probably we can't get sms no need to to try again.
                            time_to_wait_for_next_cycle = self._find_remaining_time()
                            time.sleep(time_to_wait_for_next_cycle + 2)
                            sms_reset_btn = self._find_reset_button()
                            if (sms_reset_btn == None):
                                raise Exception("We couldn't find sms button after waiting for next-cycle")
                            else:
                                sms_reset_btn.click()
                        else:
                            raise Exception("Couldn't find sms-reset button")

                if ret == LoginErrors.RE_LOGIN:
                    error("Need to re-login!")
                    continue

                time.sleep(KoineksBrowser.FIRST_SMS_CODE_WAIT_TIME)
                sms_code_entered = self.enter_sms_code()
                if (sms_code_entered != True):
                    raise Exception("couldn't enter sms code!")
                ret, error_code = self._is_login_succeed()
                if (ret):
                    return True
                else:
                    if error_code == LoginErrors.WRONG_SMS_CODE:
                        wait_time = self._find_remaining_time() - 10
                        if wait_time < 0:
                            wait_time = 0
                        user_feedback("we will try again to enter sms after waiting {:d}".format(int(wait_time)))
                        time.sleep(wait_time - 10)
                        self.enter_sms_code()
                        ret, error_code = self._is_login_succeed()
                        if (
                                ret != True):  # Sms code could not fetched even waited until last minute. which means we will not be able to get anyway.
                            raise Exception("Fatal Error on login : Error Code {:s}".format(str(error_code)))
                        else:
                            return True
                    elif error_code == LoginErrors.NEED_TO_WAIT:  # TODO: investigate after this.
                        user_feedback("Need to be wait")
                        time.sleep(KoineksBrowser.TRY_AGAIN_WAIT_TIME)

            except Exception as e:  # TODO: Handle this is better ..
                self.get_ss()
                wtf_count += 1
                error("WTF{:d}: {:s}".format(int(wtf_count), str(e)))
                login_sucess = False
                if (str(e).__contains__("Tried to run command without establishing a connection")):
                    return False
                    break;
                if (wtf_count > 2):
                    error("Too much wtf for loggin process.")
                    return False  # call destructor.



    def get_browser(self):
        return self._browser

    def fetch_balance(self,symbol:str):
        browser = self.get_browser()
        if symbol == "TRY":
            try_balance = browser.find_by_css(
                'div[class="navbar-nav ml-auto"] button[class="btn btn-outline-success bakiye-top d-sm-block"] span[class="wallet-TRY"] ')[
                0]._get_value()
            return try_balance

        spans = browser.find_by_css('span')
        index = 0
        try:
            for span in spans:
                val = span._get_value()
                if (str(val).__contains__(symbol)):
                    balance = spans[index + 1]._get_value()  # next span have the balane info!
                    try:
                        if (balance == "Yeni"):
                            balance = spans[index + 2]._get_value()
                    except Exception as e:
                        error("Error updating new added currency{:s} balance {:s}".format(str(symbol), str(e)))
                    return balance
                    break
                index = index + 1
        except Exception as e:
            error("Error occured while fetching balance , will try again error {:s}!".format(str(e)))
            return self.fetch_balance(symbol)

    def go_to_market(self,market: str, force:bool=False):
        url = KoineksBrowser.URL + "/market/" + str(market).upper() + "TRY"
        if self._browser.driver.current_url == url and force != True:
            return
        self._browser.visit(url)


    def __find_order_table(self, type: str):
        return self._browser.find_by_id("table-" + type)[0]

    def __get_tds(self, table):
        return table.find_by_css('td')

    def __fetch_tds_val(self, table):
        tds = []
        tds_val = []
        tdi = 0
        error_count = 0
        while len(tds) == 0:
            tds = self.__get_tds(table)
            if (tds != None and len(tds) > 0):
                while (tdi < 31):
                    try:
                        price = float(tds[tdi]._get_value())
                        amount = float(tds[tdi + 1]._get_value())
                        total = price * amount
                        tdi = tdi + 3  # 3 elements are got.
                        tds_val.append([price, amount, total])
                    except Exception as e:
                        error_count += 1
                        if (error_count > 5):
                            raise Exception("Too much exception trying to get tds")
                        debug(
                            "At tdi {:d} exception occured , but we will continue from where we got exception..".format(
                                int(tdi)))
                        tds = self.__get_tds(table)
                return tds_val
            else:
                error("couldn't find tds! try again ")
                time.sleep(1)
                continue
                # raise Exception("tds dom element couldn't be found")

    def __get_table_val(self):
        ask_table = self.__find_order_table("asks")
        ask_table_val = self.__fetch_tds_val(ask_table)
        bid_table = self.__find_order_table("bids")
        bid_table_val = self.__fetch_tds_val(bid_table)
        return {'asks': ask_table_val, 'bids': bid_table_val}


    def fetch_order_book(self, currency,force_go_to_market:bool=False):
        self.go_to_market(currency,force_go_to_market)
        return self.__get_table_val()


    def withdraw(self,symbol:str,amount:float,address:str,tag:str=""):
        browser = self.get_browser()

        browser.visit(KoineksBrowser.WALLET_URL)
        container = self.find_containter_for_withdraw(symbol)
        container.click()


        browser.find_by_name("transfer_address")[0]._set_value(address)
        browser.find_by_name("transfer_amount")[0]._set_value(amount)



        transfer_button = self.find_transfer_button()

        transfer_button.click()
        time.sleep(3)
        sms_code_element = browser.find_by_id('sms-code')
        sms_code_element._set_value("Fetching Sms code")
        time.sleep(KoineksBrowser.SMS_WAIT_TIME)  # wait for sms

        sms_code = KoineksService.mail_service.get_sms_verification_code()

        sms_code_element._set_value(sms_code)

        browser.find_by_id('sms-submit').click()
        time.sleep(10)  # wait for mail
        confirmation_link = KoineksService.mail_service.get_koineks_confirmation_link()

        browser.visit(confirmation_link)

        KoineksService.save_screen_shot_at(KoineksService.LOG_DIR + request.get_log_file_name() + "_result",
                                           browser)
        debug("done withdraw :)")

    def get_ss(self):
        pass

    def buy(self, symbol: str, amount: float, price: float):
        browser = self.get_browser()
        self.go_to_market(symbol)

        browser.find_by_name("price")[0]._set_value(price)
        browser.find_by_name("amount")[0]._set_value(amount)

        buy_button = self.find_buy_button()

        buy_button.click()

        debug("bought")
        self.update_balance(symbol)
        debug("{:s} balance updated!".format(str(symbol)))

    def sell(self, symbol: str, amount: float, price: float):
        browser = self.get_browser()
        self.go_to_market(symbol)
        browser.find_link_by_href('#sell').click()
        browser.find_by_name("price")[1]._set_value(price)
        browser.find_by_name("amount")[1]._set_value(amount)

        sell_button = self.find_buy_button()

        sell_button.click()

        debug("sold")
        self.update_balance(symbol)
        debug("{:s} balance updated!".format(str(symbol)))