import sys
import argparse
from .parser import ConfigParser
from .xml_converter import XMLConverter
from .exceptions import ConfigParserError

def main():
    """
    Главная функция утилиты командной строки
    """
    parser = argparse.ArgumentParser(
        description='Конвертер учебного конфигурационного языка в XML',
        prog='config-parser'
    )
    parser.add_argument(
        '-o', '--output', 
        required=True, 
        help='Путь к выходному XML файлу'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Чтение из stdin
        if sys.stdin.isatty():
            print("Ожидается ввод через стандартный поток ввода")
            print("Использование: config-parser -o output.xml < input.config")
            sys.exit(1)
            
        input_text = sys.stdin.read()
        
        if not input_text.strip():
            print("Ошибка: Входной поток пуст", file=sys.stderr)
            sys.exit(1)
        
        # Парсинг
        config_parser = ConfigParser()
        parsed_data = config_parser.parse(input_text)
        
        # Конвертация в XML
        xml_output = XMLConverter.dict_to_xml(parsed_data)
        
        # Запись в файл
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(xml_output)
        except IOError as e:
            print(f"Ошибка записи в файл {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
            
        print(f"Успешно сконвертировано в {args.output}")
        
    except ConfigParserError as e:
        print(f"Ошибка парсинга: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПрервано пользователем", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
