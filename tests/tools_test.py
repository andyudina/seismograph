import unittest
from mock import MagicMock, patch

from seismograph.ext.selenium.proxy.tools import WebElementToObject, WebElementCssToObject

class WebElemenToObjectTest(unittest.TestCase):
    TEST_ATTR = 'css'

    def setUp(self):
        self.proxy = MagicMock()
        self.proxy.parent = MagicMock()
        self.proxy._wrapped = MagicMock()
        self.proxy.parent.execute_script = MagicMock()
        self.proxy.get_attribute = MagicMock(return_value = self.TEST_ATTR)
       
        self.el = WebElementToObject(self.proxy)
 
    def test_get_attr(self):
        self.assertEqual(self.el.css, self.TEST_ATTR)
         
    def test_get_attr_alert(self):
        err = None
        self.proxy.get_attribute = MagicMock(return_value = None)
        try:
            css = self.el.css
        except AttributeError as e:
            err = e.args[0]
        self.assertEqual(err, self.TEST_ATTR)
   
    def test_set_attr(self):
        self.el.css = 'css'
        assert self.proxy.parent.execute_script.call_count == 1

class WebElemenCSSToObjectTest(unittest.TestCase):
    TEST_ATTR = 'css'

    def setUp(self):
        self.proxy = MagicMock()
        self.proxy.parent = MagicMock()
        self.proxy._wrapped = MagicMock()
        self.proxy.parent.execute_script = MagicMock()
        self.proxy.value_of_css_property = MagicMock(return_value = self.TEST_ATTR)

        self.el = WebElementCssToObject(self.proxy)

    def test_get_attr(self):
        self.assertEqual(self.el.css, self.TEST_ATTR)


    def test_set_attr(self):
        self.el.css = 'css'
        assert self.proxy.parent.execute_script.call_count == 1

if __name__ == '__main__':
    unittest.main()
