# -*- coding: utf-8 -*-

# Copyright 2012 splinter authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
import os

from selenium.webdriver import DesiredCapabilities, Firefox
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from splinter.driver.webdriver import (
    BaseWebDriver, WebDriverElement as WebDriverElement)
from splinter.driver.webdriver.cookie_manager import CookieManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options


class WebDriver(BaseWebDriver):

    driver_name = "Firefox"

    def __init__(self, profile=None, extensions=None, user_agent=None,
                 profile_preferences=None, fullscreen=False, wait_time=2,
                 timeout=90, capabilities=None, headless=False,
                 incognito=False, **kwargs):

        firefox_profile = FirefoxProfile(profile)
        firefox_profile.set_preference('extensions.logging.enabled', False)
        firefox_profile.set_preference('network.dns.disableIPv6', False)
        firefox_profile.set_preference("layout.css.devPixelsPerPx", "0.8")
        firefox_profile.set_preference("network.proxy.type", 0)

        firefox_capabilities = DesiredCapabilities().FIREFOX
        firefox_capabilities["marionette"] = True

        firefox_options = Options()

        if capabilities:
            for key, value in capabilities.items():
                firefox_capabilities[key] = value

        if user_agent is not None:
            firefox_profile.set_preference(
                'general.useragent.override', user_agent)

        if profile_preferences:
            for key, value in profile_preferences.items():
                firefox_profile.set_preference(key, value)

        if extensions:
            for extension in extensions:
                firefox_profile.add_extension(extension)

        if headless:
            os.environ.update({"MOZ_HEADLESS": '1'})
            binary = FirefoxBinary()
            binary.add_command_line_options('-headless')
            kwargs['firefox_binary'] = binary

        if incognito:
            firefox_options.add_argument('-private')

        self.driver = Firefox(firefox_profile,
                              capabilities=firefox_capabilities,
                              firefox_options=firefox_options,
                              timeout=timeout, **kwargs)

        if fullscreen:
            ActionChains(self.driver).send_keys(Keys.F11).perform()

        self.element_class = WebDriverElement

        self._cookie_manager = CookieManager(self.driver)

        super(WebDriver, self).__init__(wait_time)
