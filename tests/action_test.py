import unittest
from mock import MagicMock, patch

from seismograph.ext.selenium.proxy.actions import Alert, ActionChains, TouchActions
from selenium.webdriver.common.action_chains import ActionChains as _ActionChains
from selenium.webdriver.common.touch_actions import TouchActions as _TouchActions

class AlertTest(unittest.TestCase):
 
    def setUp(self):
        proxy = MagicMock()
        self.browser = MagicMock()
        proxy.browser = self.browser
        self.alert = Alert(proxy)
 
    def test_browser(self):
        self.assertEqual(self.alert.browser, self.browser)
 

class ActionBaseTest:

    def test_browser(self):
        self.assertEqual(self.chain.browser, self.browser)
 
    def test_reset(self):
        self.chain.reset()
        self.assertEqual(self.chain._actions, [])

    def test_exit(self):
        with patch.object(self._get_base_class(), '__exit__', return_value=None) as mock_exit:
            with self.chain:
                self.chain._actions = [1, 2, 3]
            assert mock_exit.call_count == 1
        self.assertEqual(self.chain._actions, [])
         

class ActionChainTest(unittest.TestCase, ActionBaseTest):
    def setUp(self):
        proxy = MagicMock()
        self.browser = MagicMock()
        proxy.browser = self.browser
        self.chain = self._get_test_class()(proxy)

    def _get_test_class(self):
        return ActionChains

    def  _get_base_class(self):
        return _ActionChains 

class TouchActionsTest(unittest.TestCase, ActionBaseTest):
    def setUp(self):
        proxy = MagicMock()
        self.browser = MagicMock()
        proxy.browser = self.browser
        self.chain = self._get_test_class()(proxy)

    def _get_test_class(self):
        return TouchActions

    def  _get_base_class(self):
        return _TouchActions

if __name__ == '__main__':
    unittest.main()
