import unittest
import sys
import os
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_parser.xml_converter import XMLConverter

class TestXMLConverter(unittest.TestCase):
    
    def test_simple_dict(self):
        data = {"name": "test", "value": 123}
        xml = XMLConverter.dict_to_xml(data)
        
        # Проверяем что XML валиден
        root = ET.fromstring(xml)
        self.assertEqual(root.tag, "config")
        self.assertEqual(len(root), 2)
    
    def test_nested_dict(self):
        data = {
            "server": {
                "host": "localhost",
                "port": 8080
            }
        }
        xml = XMLConverter.dict_to_xml(data)
        root = ET.fromstring(xml)
        
        server = root.find("server")
        self.assertIsNotNone(server)
        self.assertEqual(server.find("host").text, "localhost")
        self.assertEqual(server.find("port").text, "8080")
    
    def test_xml_escaping(self):
        data = {"text": "Hello <world> & 'friends'"}
        xml = XMLConverter.dict_to_xml(data)
        
        # Проверяем что специальные символы экранированы
        self.assertIn("&lt;world&gt;", xml)
        self.assertIn("&amp;", xml)
    
    def test_different_types(self):
        data = {
            "string": "text",
            "number": 42,
            "nested": {
                "value": 100
            }
        }
        xml = XMLConverter.dict_to_xml(data)
        root = ET.fromstring(xml)
        
        string_elem = root.find("string")
        self.assertEqual(string_elem.get("type"), "string")
        
        number_elem = root.find("number")
        self.assertEqual(number_elem.get("type"), "number")

if __name__ == '__main__':
    unittest.main()
