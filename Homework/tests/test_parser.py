import unittest
import sys
import os

# Добавляем src в путь для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config_parser.parser import ConfigParser
from config_parser.exceptions import SyntaxError, ConstantError

class TestConfigParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = ConfigParser()
    
    def test_simple_number(self):
        result = self.parser.parse("(test: 123;)")
        self.assertEqual(result["test"], 123)
    
    def test_simple_string(self):
        result = self.parser.parse("(test: q(hello world);)")
        self.assertEqual(result["test"], "hello world")
    
    def test_nested_dict(self):
        result = self.parser.parse("(outer: (inner: 42;);)")
        self.assertEqual(result["outer"]["inner"], 42)
    
    def test_multiple_properties(self):
        result = self.parser.parse("""
        (
            name: q(Test);
            value: 100;
            enabled: true;
        )
        """)
        self.assertEqual(result["name"], "Test")
        self.assertEqual(result["value"], 100)
    
    def test_comments(self):
        result = self.parser.parse("""
        // Однострочный комментарий
        (
            test: 123; // Еще комментарий
        )
        // Конечный комментарий
        """)
        self.assertEqual(result["test"], 123)
    
    def test_multiline_comments(self):
        result = self.parser.parse("""
        /#
        Многострочный
        комментарий
        #/
        (test: 456;)
        """)
        self.assertEqual(result["test"], 456)
    
    def test_define_constant(self):
        result = self.parser.parse("""
        define base_value 10
        (
            result: $base_value$;
        )
        """)
        self.assertEqual(result["result"], 10)
    
    def test_constant_expression(self):
        result = self.parser.parse("""
        define base 10
        (
            result: $base 5 +$;
        )
        """)
        self.assertEqual(result["result"], 15)
    
    def test_rock_function(self):
        result = self.parser.parse("(test: $рок()$;)")
        self.assertEqual(result["test"], 42)
    
    def test_complex_expression(self):
        result = self.parser.parse("""
        define a 5
        define b 10
        (
            result: $a b + 3 +$;
        )
        """)
        self.assertEqual(result["result"], 18)
    
    def test_syntax_error(self):
        with self.assertRaises(SyntaxError):
            self.parser.parse("(test: ;)")
    
    def test_unclosed_string(self):
        with self.assertRaises(SyntaxError):
            self.parser.parse("(test: q(unclosed string;)")
    
    def test_unknown_constant(self):
        with self.assertRaises(ConstantError):
            self.parser.parse("(test: $unknown$;)")

if __name__ == '__main__':
    unittest.main()
