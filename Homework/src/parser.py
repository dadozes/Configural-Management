import re
from typing import Dict, Any, List, Union
from .exceptions import SyntaxError, ConstantError

class ConfigParser:
    """
    Парсер учебного конфигурационного языка
    """
    
    def __init__(self):
        self.constants = {}
        self.pos = 0
        self.text = ""
        self.line = 1
        self.column = 1
        
    def _update_position(self, char):
        """Обновляет позицию для сообщений об ошибках"""
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
    
    def _error(self, message):
        """Создает сообщение об ошибке с позицией"""
        return SyntaxError(f"Строка {self.line}, колонка {self.column}: {message}")
        
    def skip_whitespace_and_comments(self):
        while self.pos < len(self.text):
            char = self.text[self.pos]
            
            # Пропускаем пробельные символы
            if char.isspace():
                self._update_position(char)
                self.pos += 1
                continue
                
            # Однострочные комментарии
            if self.text[self.pos:].startswith("//"):
                end_line = self.text.find("\n", self.pos)
                if end_line == -1:
                    self.pos = len(self.text)
                else:
                    # Обновляем позицию для всех символов в комментарии
                    for i in range(self.pos, end_line + 1):
                        self._update_position(self.text[i])
                    self.pos = end_line + 1
                continue
                    
            # Многострочные комментарии
            if self.text[self.pos:].startswith("/#"):
                end_comment = self.text.find("#/", self.pos)
                if end_comment == -1:
                    raise self._error("Незакрытый многострочный комментарий")
                
                # Обновляем позицию для всех символов в комментарии
                for i in range(self.pos, end_comment + 2):
                    self._update_position(self.text[i])
                self.pos = end_comment + 2
                continue
                
            break

    def parse_number(self) -> int:
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        number_str = self.text[start:self.pos]
        
        # Обновляем позицию
        for char in number_str:
            self._update_position(char)
            
        return int(number_str)

    def parse_string(self) -> str:
        if not self.text[self.pos:].startswith("q("):
            raise self._error("Ожидается q( для строки")
        
        self.pos += 2  # Пропускаем "q("
        self.column += 2
        
        start = self.pos
        depth = 1
        
        while self.pos < len(self.text) and depth > 0:
            char = self.text[self.pos]
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            self._update_position(char)
            self.pos += 1
            
        if depth > 0:
            raise self._error("Незакрытая строка")
            
        return self.text[start:self.pos-1]  # Исключаем последнюю ')'

    def parse_identifier(self) -> str:
        start = self.pos
        if self.pos < len(self.text) and (self.text[self.pos].isalpha() or self.text[self.pos] == '_'):
            self.pos += 1
            while (self.pos < len(self.text) and 
                   (self.text[self.pos].isalnum() or self.text[self.pos] == '_')):
                self.pos += 1
            identifier = self.text[start:self.pos]
            
            # Обновляем позицию
            for char in identifier:
                self._update_position(char)
                
            return identifier
        raise self._error("Ожидается идентификатор")

    def parse_value(self) -> Union[int, str, Dict[str, Any]]:
        self.skip_whitespace_and_comments()
        
        if self.pos >= len(self.text):
            raise self._error("Неожиданный конец файла")
        
        # Число
        if self.text[self.pos].isdigit():
            return self.parse_number()
            
        # Строка
        elif self.text[self.pos:].startswith("q("):
            return self.parse_string()
            
        # Словарь
        elif self.text[self.pos] == '(':
            return self.parse_dict()
            
        # Константное выражение
        elif self.text[self.pos] == '$':
            return self.parse_constant_expression()
            
        else:
            raise self._error(f"Неизвестное значение: '{self.text[self.pos]}'")

    def parse_dict(self) -> Dict[str, Any]:
        if self.text[self.pos] != '(':
            raise self._error("Ожидается ( для словаря")
            
        self._update_position('(')
        self.pos += 1
        result = {}
        
        while True:
            self.skip_whitespace_and_comments()
            
            if self.pos >= len(self.text):
                raise self._error("Неожиданный конец файла в словаре")
            
            # Конец словаря
            if self.text[self.pos] == ')':
                self._update_position(')')
                self.pos += 1
                break
                
            # Парсим имя
            name = self.parse_identifier()
            
            self.skip_whitespace_and_comments()
            
            # Двоеточие
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise self._error("Ожидается : после имени")
            self._update_position(':')
            self.pos += 1
            
            self.skip_whitespace_and_comments()
            
            # Значение
            value = self.parse_value()
            result[name] = value
            
            self.skip_whitespace_and_comments()
            
            # Точка с запятой
            if self.pos < len(self.text) and self.text[self.pos] == ';':
                self._update_position(';')
                self.pos += 1
            else:
                # Проверяем, не конец ли словаря
                if self.pos < len(self.text) and self.text[self.pos] == ')':
                    continue
                raise self._error("Ожидается ; после значения")
                
        return result

    def parse_constant_expression(self) -> Any:
        if self.text[self.pos] != '$':
            raise self._error("Ожидается $ для константного выражения")
            
        self._update_position('$')
        self.pos += 1
        self.skip_whitespace_and_comments()
        
        # Парсим первый операнд
        if self.text[self.pos].isdigit():
            operand1 = self.parse_number()
        else:
            name = self.parse_identifier()
            if name not in self.constants:
                raise ConstantError(f"Неизвестная константа: {name}")
            operand1 = self.constants[name]
        
        self.skip_whitespace_and_comments()
        
        # Операции
        while self.pos < len(self.text) and self.text[self.pos] != '$':
            if self.text[self.pos] == '+':
                self._update_position('+')
                self.pos += 1
                self.skip_whitespace_and_comments()
                
                # Парсим второй операнд
                if self.text[self.pos].isdigit():
                    operand2 = self.parse_number()
                else:
                    name = self.parse_identifier()
                    if name not in self.constants:
                        raise ConstantError(f"Неизвестная константа: {name}")
                    operand2 = self.constants[name]
                    
                operand1 += operand2
                
            elif self.text[self.pos:].startswith("рок()"):
                for char in "рок()":
                    self._update_position(char)
                self.pos += 5
                # Простая реализация рок() - возвращает 42
                operand1 = 42
                
            else:
                raise self._error(f"Неизвестная операция: '{self.text[self.pos]}'")
            
            self.skip_whitespace_and_comments()
        
        # Закрывающий $
        if self.pos >= len(self.text) or self.text[self.pos] != '$':
            raise self._error("Ожидается $ в конце константного выражения")
        self._update_position('$')
        self.pos += 1
        
        return operand1

    def parse_define(self):
        if not self.text[self.pos:].startswith("define"):
            raise self._error("Ожидается define")
            
        for char in "define":
            self._update_position(char)
        self.pos += 6
        self.skip_whitespace_and_comments()
        
        name = self.parse_identifier()
        self.skip_whitespace_and_comments()
        
        value = self.parse_value()
        self.constants[name] = value
        
        return {"type": "define", "name": name, "value": value}

    def parse(self, text: str) -> Dict[str, Any]:
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.constants = {}
        result = {}
        
        while self.pos < len(self.text):
            self.skip_whitespace_and_comments()
            
            if self.pos >= len(self.text):
                break
                
            # Обработка define
            if self.text[self.pos:].startswith("define"):
                self.parse_define()
                
            # Словарь (основная структура)
            elif self.text[self.pos] == '(':
                dict_result = self.parse_dict()
                # Если это корневой словарь, возвращаем его
                if not result:
                    result = dict_result
                    
            else:
                raise self._error(f"Неизвестная конструкция: '{self.text[self.pos]}'")
                
        return result
