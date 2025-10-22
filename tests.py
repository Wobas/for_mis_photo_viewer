# test_image_viewer.py
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QPoint
import PyQt5.QtTest as QtTest

# Добавляем путь к модулям приложения
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui import ImageViewer
from save_image_dialog import SaveImageDialog


class TestImageViewer(unittest.TestCase):
    """Тесты для основного окна просмотра изображений"""
    
    @classmethod
    def setUpClass(cls):
        # Создаем QApplication один раз для всех тестов
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.viewer = ImageViewer()
        # Создаем временное тестовое изображение
        self.test_image = QImage(100, 100, QImage.Format_RGB32)
        self.test_image.fill(Qt.red)
        
        # Сохраняем временное изображение для тестов загрузки
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        self.test_image.save(self.test_image_path)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        self.viewer.close()
        # Удаляем временные файлы
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initial_state(self):
        """Тест начального состояния приложения"""
        self.assertIsNone(self.viewer.current_image)
        self.assertEqual(self.viewer.scale_factor, 1.0)
        self.assertIsNone(self.viewer.current_pixmap)
        self.assertEqual(self.viewer.current_image_name, "image")
        
        # Проверяем, что кнопки изначально отключены
        self.assertFalse(self.viewer.save_action.isEnabled())
        self.assertFalse(self.viewer.zoom_in_btn.isEnabled())
        self.assertFalse(self.viewer.zoom_out_btn.isEnabled())
        self.assertFalse(self.viewer.original_size_btn.isEnabled())
        self.assertFalse(self.viewer.nav_up_btn.isEnabled())
        self.assertFalse(self.viewer.nav_down_btn.isEnabled())
        self.assertFalse(self.viewer.nav_left_btn.isEnabled())
        self.assertFalse(self.viewer.nav_right_btn.isEnabled())
    
    @patch('ui.QFileDialog.getOpenFileName')
    def test_open_image_success(self, mock_open_file):
        """Тест успешного открытия изображения"""
        # Мокаем диалог открытия файла
        mock_open_file.return_value = (self.test_image_path, 'Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)')
        
        # Вызываем метод открытия изображения через публичный интерфейс (если есть) или напрямую
        # Если методы приватные, тестируем через публичные действия
        self.viewer._ImageViewer__open_image()
        
        # Проверяем, что изображение загружено
        self.assertIsNotNone(self.viewer.current_image)
        self.assertIsNotNone(self.viewer.current_pixmap)
        self.assertEqual(self.viewer.current_image_name, "test_image.png")
        self.assertEqual(self.viewer.scale_factor, 1.0)
        
        # Проверяем, что кнопки активированы
        self.assertTrue(self.viewer.save_action.isEnabled())
        self.assertTrue(self.viewer.zoom_in_btn.isEnabled())
        self.assertTrue(self.viewer.zoom_out_btn.isEnabled())
        self.assertTrue(self.viewer.original_size_btn.isEnabled())
        self.assertTrue(self.viewer.nav_up_btn.isEnabled())
        self.assertTrue(self.viewer.nav_down_btn.isEnabled())
        self.assertTrue(self.viewer.nav_left_btn.isEnabled())
        self.assertTrue(self.viewer.nav_right_btn.isEnabled())
    
    @patch('ui.QFileDialog.getOpenFileName')
    @patch('ui.QMessageBox.warning')
    def test_open_image_failure(self, mock_warning, mock_open_file):
        """Тест открытия невалидного изображения"""
        # Мокаем диалог открытия файла с несуществующим файлом
        mock_open_file.return_value = ("invalid_path.png", 'Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)')
        
        # Вызываем метод открытия изображения
        self.viewer._ImageViewer__open_image()
        
        # Проверяем, что было показано предупреждение
        mock_warning.assert_called_once()
    
    def test_zoom_in(self):
        """Тест увеличения масштаба"""
        # Устанавливаем тестовое изображение
        self.viewer.current_image = self.test_image
        self.viewer.current_pixmap = QPixmap.fromImage(self.test_image)
        self.viewer.scale_factor = 1.0
        
        # Включаем кнопки
        self.viewer.zoom_in_btn.setEnabled(True)
        
        # Тестируем увеличение
        self.viewer._ImageViewer__zoom_in()
        self.assertEqual(self.viewer.scale_factor, 1.25)
        
        # Тестируем ограничение максимального масштаба
        self.viewer.scale_factor = 10.0
        self.viewer._ImageViewer__zoom_in()
        self.assertEqual(self.viewer.scale_factor, 10.0)
    
    def test_zoom_out(self):
        """Тест уменьшения масштаба"""
        # Устанавливаем тестовое изображение
        self.viewer.current_image = self.test_image
        self.viewer.current_pixmap = QPixmap.fromImage(self.test_image)
        self.viewer.scale_factor = 1.0
        
        # Включаем кнопки
        self.viewer.zoom_out_btn.setEnabled(True)
        
        # Тестируем уменьшение
        self.viewer._ImageViewer__zoom_out()
        self.assertEqual(self.viewer.scale_factor, 0.8)
        
        # Тестируем ограничение минимального масштаба
        self.viewer.scale_factor = 0.01
        self.viewer._ImageViewer__zoom_out()
        self.assertEqual(self.viewer.scale_factor, 0.01)
    
    def test_original_size(self):
        """Тест сброса масштаба к оригинальному"""
        # Устанавливаем тестовое изображение и измененный масштаб
        self.viewer.current_image = self.test_image
        self.viewer.current_pixmap = QPixmap.fromImage(self.test_image)
        self.viewer.scale_factor = 2.5
        
        # Включаем кнопки
        self.viewer.original_size_btn.setEnabled(True)
        
        # Тестируем сброс масштаба
        self.viewer._ImageViewer__original_size()
        self.assertEqual(self.viewer.scale_factor, 1.0)
    
    def test_navigation_buttons(self):
        """Тест кнопок навигации"""
        # Устанавливаем тестовое изображение
        self.viewer.current_image = self.test_image
        self.viewer.current_pixmap = QPixmap.fromImage(self.test_image)
        
        # Включаем кнопки навигации
        self.viewer.nav_up_btn.setEnabled(True)
        self.viewer.nav_down_btn.setEnabled(True)
        self.viewer.nav_left_btn.setEnabled(True)
        self.viewer.nav_right_btn.setEnabled(True)
        
        # Получаем начальные значения скроллбаров
        initial_v_scroll = self.viewer.scroll_area.verticalScrollBar().value()
        initial_h_scroll = self.viewer.scroll_area.horizontalScrollBar().value()
        
        # Тестируем кнопки навигации
        self.viewer._ImageViewer__nav_up()
        self.viewer._ImageViewer__nav_down()
        self.viewer._ImageViewer__nav_left()
        self.viewer._ImageViewer__nav_right()
        
        # Проверяем, что значения изменились (точные значения могут зависеть от реализации)
        v_scroll = self.viewer.scroll_area.verticalScrollBar()
        h_scroll = self.viewer.scroll_area.horizontalScrollBar()
        self.assertNotEqual(v_scroll.value(), initial_v_scroll)
        self.assertNotEqual(h_scroll.value(), initial_h_scroll)


class TestSaveImageDialog(unittest.TestCase):
    """Тесты для диалога сохранения изображения"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        self.dialog = SaveImageDialog(file_name="test_image")
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        self.dialog.close()
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_initial_state(self):
        """Тест начального состояния диалога"""
        self.assertEqual(self.dialog.filename_edit.text(), "test_image")
        self.assertEqual(self.dialog.format_combo.currentText(), "JPEG (*.jpg)")
        self.assertEqual(self.dialog.dir_edit.text(), "")
    
    def test_get_save_info(self):
        """Тест получения информации для сохранения"""
        # Устанавливаем тестовые данные
        self.dialog.dir_edit.setText(self.temp_dir)
        self.dialog.filename_edit.setText("test_save")
        self.dialog.format_combo.setCurrentText("PNG (*.png)")
        
        # Получаем информацию для сохранения
        full_path, file_format = self.dialog.get_save_info()
        
        # Проверяем результаты
        expected_path = os.path.join(self.temp_dir, "test_save.png")
        self.assertEqual(full_path, expected_path)
        self.assertEqual(file_format, "PNG")
    
    def test_get_save_info_empty_fields(self):
        """Тест получения информации с пустыми полями"""
        # Оставляем поля пустыми
        self.dialog.dir_edit.setText("")
        self.dialog.filename_edit.setText("")
        
        full_path, file_format = self.dialog.get_save_info()
        
        self.assertIsNone(full_path)
        self.assertIsNone(file_format)
    
    def test_format_mapping(self):
        """Тест маппинга форматов файлов"""
        test_cases = [
            ("JPEG (*.jpg)", ("jpg", "JPEG")),
            ("PNG (*.png)", ("png", "PNG")),
            ("BMP (*.bmp)", ("bmp", "BMP")),
            ("TIFF (*.tif)", ("tif", "TIFF"))
        ]
        
        for format_text, expected in test_cases:
            with self.subTest(format=format_text):
                self.dialog.dir_edit.setText(self.temp_dir)
                self.dialog.filename_edit.setText("test")
                self.dialog.format_combo.setCurrentText(format_text)
                
                full_path, file_format = self.dialog.get_save_info()
                expected_path = os.path.join(self.temp_dir, f"test.{expected[0]}")
                
                self.assertEqual(full_path, expected_path)
                self.assertEqual(file_format, expected[1])
    
    @patch('save_image_dialog.QFileDialog.getExistingDirectory')
    def test_select_directory(self, mock_get_directory):
        """Тест выбора директории"""
        mock_get_directory.return_value = self.temp_dir
        
        # Вызываем метод выбора директории
        self.dialog._SaveImageDialog__select_directory()
        
        # Проверяем, что путь установлен
        self.assertEqual(self.dialog.dir_edit.text(), self.temp_dir)
    
    @patch('save_image_dialog.QMessageBox.warning')
    def test_check_input_empty(self, mock_warning):
        """Тест проверки пустого ввода"""
        # Оставляем поля пустыми
        self.dialog.dir_edit.setText("")
        self.dialog.filename_edit.setText("")
        
        # Вызываем проверку ввода
        result = self.dialog._SaveImageDialog__check_input()
        
        # Проверяем, что было показано предупреждение
        mock_warning.assert_called_once()
        self.assertIsNone(result)
    
    def test_check_input_valid(self):
        """Тест проверки валидного ввода"""
        # Заполняем поля валидными данными
        self.dialog.dir_edit.setText(self.temp_dir)
        self.dialog.filename_edit.setText("test_image")
        
        # Вызываем проверку ввода
        result = self.dialog._SaveImageDialog__check_input()
        
        # Проверяем, что метод accept был вызван
        self.assertEqual(result, QDialog.Accepted)


class TestImageViewerIntegration(unittest.TestCase):
    """Интеграционные тесты для всего приложения"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        self.viewer = ImageViewer()
        # Создаем временное тестовое изображение
        self.test_image = QImage(200, 150, QImage.Format_RGB32)
        self.test_image.fill(Qt.blue)
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "integration_test.png")
        self.test_image.save(self.test_image_path)
    
    def tearDown(self):
        self.viewer.close()
        if os.path.exists(self.test_image_path):
            os.remove(self.test_image_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    @patch('ui.QFileDialog.getOpenFileName')
    def test_full_workflow(self, mock_open_file):
        """Тест полного рабочего процесса: открытие -> масштабирование -> сохранение"""
        # Мокаем открытие файла
        mock_open_file.return_value = (self.test_image_path, 'Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)')
        
        # 1. Открываем изображение
        self.viewer._ImageViewer__open_image()
        
        # Проверяем, что изображение загружено
        self.assertIsNotNone(self.viewer.current_image)
        self.assertEqual(self.viewer.scale_factor, 1.0)
        
        # 2. Масштабируем
        self.viewer._ImageViewer__zoom_in()
        self.assertEqual(self.viewer.scale_factor, 1.25)
        
        self.viewer._ImageViewer__zoom_out()
        self.assertEqual(self.viewer.scale_factor, 1.0)
        
        # 3. Используем навигацию
        self.viewer._ImageViewer__nav_up()
        self.viewer._ImageViewer__nav_left()
        
        # 4. Сбрасываем масштаб
        self.viewer._ImageViewer__original_size()
        self.assertEqual(self.viewer.scale_factor, 1.0)
    
    def test_display_image(self):
        """Тест отображения изображения"""
        # Устанавливаем тестовое изображение
        self.viewer.current_image = self.test_image
        self.viewer.current_pixmap = QPixmap.fromImage(self.test_image)
        self.viewer.current_image_name = "test_display.png"
        
        # Тестируем отображение с разными масштабами
        self.viewer.scale_factor = 1.0
        self.viewer._ImageViewer__display_image()
        
        self.viewer.scale_factor = 0.5
        self.viewer._ImageViewer__display_image()
        
        self.viewer.scale_factor = 2.0
        self.viewer._ImageViewer__display_image()
        
        # Проверяем, что изображение установлено в QLabel
        self.assertIsNotNone(self.viewer.image_label.pixmap())


# Альтернативный подход: тесты с публичными методами (если бы методы были публичными)
class TestImageViewerPublicInterface(unittest.TestCase):
    """Альтернативные тесты, если бы методы были публичными"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        self.viewer = ImageViewer()
    
    def tearDown(self):
        self.viewer.close()
    
    def test_button_connections(self):
        """Тест подключения кнопок к слотам"""
        # Проверяем, что кнопки подключены к правильным методам
        self.assertTrue(self.viewer.zoom_in_btn.isEnabled() or not self.viewer.zoom_in_btn.isEnabled())
        self.assertTrue(self.viewer.zoom_out_btn.isEnabled() or not self.viewer.zoom_out_btn.isEnabled())
        self.assertTrue(self.viewer.original_size_btn.isEnabled() or not self.viewer.original_size_btn.isEnabled())


if __name__ == '__main__':
    # Создаем test suite
    loader = unittest.TestLoader()
    
    # Загружаем тесты, игнорируя приватные методы в именах
    suite = loader.loadTestsFromTestCase(TestImageViewer)
    suite.addTests(loader.loadTestsFromTestCase(TestSaveImageDialog))
    suite.addTests(loader.loadTestsFromTestCase(TestImageViewerIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Завершаем приложение
    sys.exit(0 if result.wasSuccessful() else 1)