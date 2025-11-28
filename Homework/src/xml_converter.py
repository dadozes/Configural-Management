import xml.etree.ElementTree as ET
from typing import Dict, Any
from .exceptions import XMLConversionError

class XMLConverter:
    """
    Конвертер данных в XML формат
    """
    
    @staticmethod
    def escape_xml_text(text: str) -> str:
        """Экранирует специальные XML символы"""
        escape_map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        return ''.join(escape_map.get(c, c) for c in text)
    
    @staticmethod
    def dict_to_xml(data: Dict[str, Any], root_name: str = "config") -> str:
        """
        Конвертирует словарь в XML строку
        
        Args:
            data: Словарь с данными
            root_name: Имя корневого элемента
            
        Returns:
            XML строка
        """
        try:
            root = ET.Element(root_name)
            
            def add_elements(parent, data_dict):
                for key, value in data_dict.items():
                    if isinstance(value, dict):
                        child = ET.SubElement(parent, key)
                        add_elements(child, value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                child = ET.SubElement(parent, key)
                                add_elements(child, item)
                            else:
                                elem = ET.SubElement(parent, key)
                                elem.text = str(item)
                    else:
                        elem = ET.SubElement(parent, key)
                        if isinstance(value, str):
                            elem.set("type", "string")
                            elem.text = XMLConverter.escape_xml_text(value)
                        elif isinstance(value, int):
                            elem.set("type", "number")
                            elem.text = str(value)
                        elif isinstance(value, bool):
                            elem.set("type", "boolean")
                            elem.text = str(value).lower()
                        else:
                            elem.text = str(value)
            
            add_elements(root, data)
            
            # Форматируем XML с отступами
            from xml.dom import minidom
            rough_string = ET.tostring(root, encoding='utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ")
            
        except Exception as e:
            raise XMLConversionError(f"Ошибка конвертации в XML: {e}")
