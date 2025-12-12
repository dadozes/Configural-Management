import sys
import xml.etree.ElementTree as ET
import re


class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse_define(self, line):
        """Обработка объявления констант (define имя значение)"""
        match = re.match(r'\(define\s+(\w+)\s+(.+)\)', line.strip())
        if match:
            name, value = match.groups()
            # Убираем кавычки если есть
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("q(") and value.endswith(")"):
                value = value[2:-1]
            else:
                try:
                    value = int(value)
                except ValueError:
                    pass
            self.constants[name] = value
            return True
        return False

    def parse_constant_expression(self, expr):
        """Обработка константных выражений $имя 1 +$"""
        expr = expr.strip('$ ')
        parts = expr.split()
        if len(parts) == 3 and parts[1].isdigit() and parts[2] == '+':
            var_name = parts[0]
            if var_name in self.constants:
                return self.constants[var_name] + int(parts[1])
        return expr

    def parse_value(self, value_str):
        """Парсинг значения"""
        value_str = value_str.strip()

        # Константное выражение
        if value_str.startswith('$') and value_str.endswith('$'):
            return self.parse_constant_expression(value_str)

        # Строка q(...)
        if value_str.startswith('q(') and value_str.endswith(')'):
            return value_str[2:-1]

        # Число
        if value_str.isdigit():
            return int(value_str)

        # Имя константы
        if value_str in self.constants:
            return self.constants[value_str]

        return value_str

    def parse_dict(self, lines, start_idx):
        """Парсинг словаря { ... }"""
        result = {}
        i = start_idx

        while i < len(lines):
            line = lines[i].strip()

            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('"') or line.startswith('/#'):
                i += 1
                continue

            # Конец словаря
            if line == '}':
                return result, i

            # Элемент словаря: имя : значение;
            if ':' in line:
                # Убираем точку с запятой в конце
                line = line.rstrip(';')
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value_str = parts[1].strip()

                    # Если значение - вложенный словарь
                    if value_str == '{':
                        nested_dict, i = self.parse_dict(lines, i + 1)
                        result[key] = nested_dict
                    else:
                        result[key] = self.parse_value(value_str)

            i += 1

        return result, i

    def parse(self, text):
        """Основной метод парсинга"""
        lines = text.strip().split('\n')
        result = {}
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Пропускаем пустые строки
            if not line:
                i += 1
                continue

            # Однострочный комментарий
            if line.startswith('"'):
                i += 1
                continue

            # Многострочный комментарий
            if line.startswith('/#'):
                while i < len(lines) and not lines[i].strip().endswith('#/'):
                    i += 1
                i += 1
                continue

            # Объявление константы
            if line.startswith('(define'):
                self.parse_define(line)
                i += 1
                continue

            # Начало основного словаря
            if line == '{':
                result, i = self.parse_dict(lines, i + 1)
                break

            i += 1

        return result


def dict_to_xml(d, parent=None, root_name="config"):
    """Рекурсивное преобразование словаря в XML"""
    if parent is None:
        root = ET.Element(root_name)
        dict_to_xml(d, root)
        return ET.ElementTree(root)

    for key, value in d.items():
        if isinstance(value, dict):
            child = ET.SubElement(parent, key)
            dict_to_xml(value, child)
        else:
            child = ET.SubElement(parent, key)
            child.text = str(value)

    return parent


def main():

    # Встроенный тестовый конфиг с разными конструкциями
    test_config = '''
" Это однострочный комментарий о сервере

(define port 8080)
(define host "localhost")
(define base_path q(/var/www))

/#
Это многострочный комментарий
описывающий конфигурацию
#/

{
    server : {
        " комментарий внутри
        address : q(localhost);
        port : $port 1 +$;
        protocol : q(http);
        paths : {
            root : $base_path$;
            logs : q(/var/log);
        };
    };

    database : {
        name : q(test_db);
        users : 5;
        " настройки соединения
        connection : {
            host : $host$;
            port : 5432;
            timeout : 30;
        };
    };

    features : {
        caching : 1;
        logging : q(debug);
        max_connections : 100;
    };
}
'''

    print("Демо-версия парсера конфигурационного языка")
    print("=" * 50)

    # Парсим конфигурацию
    parser = ConfigParser()
    config_dict = parser.parse(test_config)

    print("\nРаспарсенные константы:")
    for name, value in parser.constants.items():
        print(f"  {name} = {value}")

    print("\nСтруктура конфигурации:")

    def print_dict(d, indent=0):
        for key, value in d.items():
            if isinstance(value, dict):
                print(" " * indent + f"{key}:")
                print_dict(value, indent + 2)
            else:
                print(" " * indent + f"{key}: {value}")

    print_dict(config_dict)

    # Преобразуем в XML
    xml_tree = dict_to_xml(config_dict, root_name="configuration")

    # Сохраняем в файл
    output_file = "config_output.xml"
    xml_tree.write(output_file, encoding="utf-8", xml_declaration=True)

    # Красиво форматируем XML
    from xml.dom import minidom
    xml_str = xml_tree.getroot()
    pretty_xml = minidom.parseString(ET.tostring(xml_str)).toprettyxml(indent="  ")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    print("\n" + "=" * 50)
    print(f"XML успешно сохранён в файл: {output_file}")
    print("\nСодержимое XML файла:")
    print("-" * 30)

    # Выводим содержимое XML
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Показываем только первые 20 строк для краткости
        lines = content.split('\n')
        for i, line in enumerate(lines[:25]):
            print(line)
        if len(lines) > 25:
            print("... (файл обрезан для отображения)")

    print("\nПрограмма завершена успешно!")

    # Дополнительный тест: пример с ошибкой
    print("\n" + "=" * 50)
    print("Дополнительный тест с ошибкой синтаксиса:")

    error_config = '''
{
    server : {
        address : q(localhost)
        " пропущена точка с запятой
        port : 8080;
    };
}
'''

    try:
        parser2 = ConfigParser()
        result = parser2.parse(error_config)
        print("Конфигурация распарсена успешно")
    except Exception as e:
        print(f"Обнаружена ошибка: {e}")


if __name__ == "__main__":
    main()
