import unittest
import sys
import os

def run_all_tests():
    """Запускает все тесты проекта"""
    
    # Добавляем корневую директорию в путь
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_path = os.path.join(project_root, 'src')
    tests_path = os.path.join(project_root, 'tests')
    
    sys.path.insert(0, src_path)
    sys.path.insert(0, tests_path)
    
    # Находим и запускаем все тесты
    loader = unittest.TestLoader()
    start_dir = tests_path
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("Запуск всех тестов проекта...")
    success = run_all_tests()
    sys.exit(0 if success else 1)
