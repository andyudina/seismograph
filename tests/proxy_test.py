import types

import unittest
from mock import MagicMock, patch
import time
from collections import OrderedDict
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

from seismograph.ext.selenium.proxy.proxy import factory_method, WebElementList, WebElementProxy, WebDriverProxy
from seismograph.utils.common import waiting_for

from seismograph.ext.selenium.polling import PollingTimeoutExceeded



class WebElementListTest(unittest.TestCase):

    def setUp(self):
        self.browser = MagicMock()
        self.config = MagicMock()
        self.reason_storage = OrderedDict()
        self.list = WebElementList(self.browser, self.config, self.reason_storage)
        for el in [{'key': 'val', 'id': 1}, {'key': 'val2', 'id': 2}, {'key': 'val', 'id': 3}]:
            el_m = MagicMock(el)
            el_m.key = MagicMock()
            el_m.attr = MagicMock()
            el_m.attr.key = el['key']
            el_m.id = MagicMock(return_value = el['id'])
            self.list.append(el_m)
 
    def test_browser_prop(self):
        self.assertEqual(self.list.browser, self.browser)
        
    def test_browser_prop(self):
        self.assertEqual(self.list.config, self.config)

    def test_reason_prop(self):
        self.assertEqual(self.list.reason_storage, self.reason_storage)

    def test_filter(self):
        filtered = [el for el in self.list.filter(key='val')]
        self.assertEqual(len(filtered) , 2)
        self.assertEqual(filtered[0].id(), 1)
        self.assertEqual(filtered[1].id(), 3) 
        
    def test_get_by(self):
        el = self.list.get_by(key='val2')
        self.assertEqual(el.id(), 2)      

    def test_stop_iteration(self):
        def side_effect(*args, **kwargs):
            raise StopIteration
        self.list.filter = MagicMock(side_effect=side_effect) 
        self.assertIsNone(self.list.get_by(key='val2'))       

class WebElementProxyTest(unittest.TestCase):
    TEST_TEXT = 'aaaaa'

    def setUp(self):
       self.browser = MagicMock()
       self.browser.action_chains = MagicMock()
       self.browser.action_chains.__enter__ = MagicMock(return_value=self.browser.action_chains)
       self.browser.action_chains.double_click = MagicMock()
       self.browser.action_chains.context_click = MagicMock()
       self.config = MagicMock()
       parent_for_we = MagicMock()
       id_for_we = MagicMock()
       self.wrapped = WebElement(parent_for_we, id_for_we)
       self.el = WebElementProxy(self.wrapped, config=self.config, browser=self.browser)
   
    def test_css(self):
       self.assertEqual(self.el.css.__class__.__name__, 'WebElementCssToObject')
    
    def test_attr(self):
       self.assertEqual(self.el.attr.__class__.__name__, 'WebElementToObject')

    def test_is_web_el(self):
       self.assertEqual(self.el.is_web_element, True)
    
    def test_double_click(self):
       self.el.double_click()
       self.assertEqual(self.browser.action_chains.double_click.call_count, 1)

    def test_context_click(self):
       self.el.context_click()
       self.assertEqual(self.browser.action_chains.context_click.call_count, 1)
    
    @patch('seismograph.ext.selenium.proxy.proxy.WebElementProxy.allow_polling')
    @patch('selenium.webdriver.remote.webelement.WebElement.text')
    def test_text_property(self, text, allow_polling):
       text.__get__ = MagicMock(return_value=self.TEST_TEXT)
       allow_polling.__get__ = MagicMock(return_value=False)
       self.assertEqual(self.el.text, self.TEST_TEXT)
        

    def test_length_with_type_err(self):
        self.assertEqual(len(self.el), 0)

    def test_repr(self):
       self.assertEqual(repr(self.el), repr(self.wrapped))

    def test_dir(self):
       self.assertIn('find_element_by_id',  dir(self.el))

class WebDriverProxyTest(unittest.TestCase):

    TEST_URL = 'http://localhost/test/'
    TEST_TEXT = 'bbbb'
    TEST_STR_ITEM = 'test'

    def setUp(self):
       self.browser = MagicMock()
       self.browser.action_chains = MagicMock()
       self.browser.touch_actions = MagicMock()

       self.config = MagicMock()
       self.config.POLLING_TIMEOUT = 1
       self.config.POLLING_DELAY = 1
       self.config.PROJECT_URL = 'http://localhost'
       with patch.object(WebDriver, '__init__', return_value=None) as mock_method:
           self.wrapped = WebDriver(command_executor= self.TEST_URL)
           self.wrapped.item = self.TEST_STR_ITEM

           parent_for_we = MagicMock()
           id_for_we = MagicMock()
           def get_web_el(*args, **kwargs):
               return WebElement(parent_for_we, id_for_we)
           self.wrapped.func = types.MethodType(get_web_el, self.wrapped)

           def get_web_el_list(*args, **kwargs):
               return [WebElement(parent_for_we, id_for_we)] * 3
           self.wrapped.func_list = types.MethodType(get_web_el_list, self.wrapped)

           def get_dummy_obj(*args, **kwargs):
               return self.TEST_STR_ITEM
           self.wrapped.func_dummy = types.MethodType(get_dummy_obj, self.wrapped)

           self.el = WebDriverProxy(self.wrapped, config=self.config, browser=self.browser)



    def test_browser(self):
       self.assertEqual(self.el.browser, self.el)
       
    def test_is_web_el(self):
       self.assertEqual(self.el.is_web_element, False)


    def test_current_url(self):
       with patch('seismograph.ext.selenium.polling.do', return_value = lambda: self.TEST_URL) as do_method:
           self.assertEqual(self.el.current_url, self.TEST_URL)
           self.assertEqual(do_method.call_count, 1)

    @patch('seismograph.ext.selenium.proxy.proxy.WebDriverProxy.current_url') 
    def test_current_path(self, current_url):
       current_url.__get__ = MagicMock(return_value=self.TEST_URL)
       self.assertEqual(self.el.current_path, '/test/')
     
    def test_runtime_error_in_curr_path(self):
       self.el.config.PROJECT_URL = None
       err = False
       try:
           self.el.current_path
       except RuntimeError as e:
           err = True
       self.assertEqual(err, True)

    def test_do_polling(self):
        with patch('seismograph.ext.selenium.polling.do', return_value = lambda: None) as do_method:
            self.el.do_polling(lambda: None,  exceptions=[])
            self.assertEqual(do_method.call_count, 1)

    def test_waiting_for(self):
        self.assertEquals(self.el.waiting_for(lambda: 1, timeout=1, delay=None), 1)
        try:
            self.el.waiting_for(lambda: None, timeout=1, delay=None)
        except PollingTimeoutExceeded as e:
            err = True
        self.assertEqual(err, True)
        self.assertEquals(e.message, 'Wait timeout "1" has been exceeded')
        self.assertEquals(self.el.waiting_for(lambda: 1), waiting_for(lambda :1))

    def test_disable_polling(self):
        with self.el.disable_polling():
            self.assertEqual(self.el.allow_polling, False)
        self.assertEqual(self.el.allow_polling, True)
 
    def test_getattr_from_webdriver_or_webelemen(self):
       self.assertEqual(self.el.__getattr_from_webdriver_or_webelement__('item'), self.TEST_STR_ITEM)

    @patch('seismograph.ext.selenium.proxy.proxy.WebDriverProxy.allow_polling')
    def test_factory_func(self, allow_polling):
       allow_polling.__get__ = MagicMock(return_value=False)
       factory_method = self.el.__getattr_from_webdriver_or_webelement__('func')
       assert callable(factory_method)
       assert isinstance(factory_method(), WebElementProxy)
       
    @patch('seismograph.ext.selenium.proxy.proxy.WebDriverProxy.allow_polling')
    def test_factory_func_list(self, allow_polling):
       allow_polling.__get__ = MagicMock(return_value=False)
       factory_method = self.el.__getattr_from_webdriver_or_webelement__('func_list')
       assert callable(factory_method)
       assert isinstance(factory_method(), WebElementList)

    @patch('seismograph.ext.selenium.proxy.proxy.WebDriverProxy.allow_polling')
    def test_factory_func_dummy(self, allow_polling):
       allow_polling.__get__ = MagicMock(return_value=False)
       factory_method = self.el.__getattr_from_webdriver_or_webelement__('func_dummy')
       assert callable(factory_method)
       self.assertEqual(factory_method(), self.TEST_STR_ITEM)

    def test_touch_actions(self):
       self.assertEqual(self.el.touch_actions.__class__.__name__, 'TouchActions')

    def test_action_chains(self):
       self.assertEqual(self.el.action_chains.__class__.__name__, 'ActionChains')

    def test_alert(self):
       self.assertEqual(self.el.alert.__class__.__name__, 'Alert')

    def test_bool(self):
       self.assertEqual(bool(self.el), True)



if __name__ == '__main__':
    unittest.main()

