class ConfigParserError(Exception):
    """Базовое исключение для парсера конфигураций"""
    pass

class SyntaxError(ConfigParserError):
    """Синтаксическая ошибка в конфигурационном файле"""
    pass

class ConstantError(ConfigParserError):
    """Ошибка в константных выражениях"""
    pass

class XMLConversionError(ConfigParserError):
    """Ошибка при конвертации в XML"""
    pass
