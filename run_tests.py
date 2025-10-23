import sys
import os
import unittest

def run_tests():
    """Запуск всех тестов"""
    # Добавляем текущую директорию в путь для импорта модулей
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("Запуск тестов программы просмотра изображений...")
    print(f"Текущая директория: {current_dir}")
    
    try:
        # Находим все тестовые файлы
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover(current_dir, pattern='tests*.py')
        
        # Запускаем тесты
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        
        print(f"\nРезультат тестов: {'УСПЕХ' if result.wasSuccessful() else 'НЕУДАЧА'}")
        print(f"Тестов выполнено: {result.testsRun}")
        print(f"Ошибок: {len(result.errors)}")
        print(f"Провалов: {len(result.failures)}")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"Ошибка при запуске тестов: {e}")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)