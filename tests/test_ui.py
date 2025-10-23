import pytest
import os
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QScrollBar
from unittest.mock import Mock, patch, MagicMock
import sys

class TestImageViewer:
    
    def test_initialization(self, image_viewer):
        """Тест инициализации окна просмотра изображений"""
        assert image_viewer.windowTitle() == 'Просмотр изображений'
        assert image_viewer.current_image is None
        assert image_viewer.scale_factor == 1.0
        assert not image_viewer.dragging
        assert image_viewer.last_mouse_pos is None
        
    def test_ui_elements_initial_state(self, image_viewer):
        """Тест начального состояния элементов UI"""
        assert not image_viewer.save_action.isEnabled()
        assert not image_viewer.zoom_in_btn.isEnabled()
        assert not image_viewer.zoom_out_btn.isEnabled()
        assert not image_viewer.original_size_btn.isEnabled()
        assert not image_viewer.nav_up_btn.isEnabled()
        assert not image_viewer.nav_down_btn.isEnabled()
        assert not image_viewer.nav_left_btn.isEnabled()
        assert not image_viewer.nav_right_btn.isEnabled()

    @patch('app.ui.QFileDialog.getOpenFileName')
    @patch('app.ui.MyImage')
    def test_open_image_success(self, mock_my_image, mock_get_open_file_name, image_viewer):
        """Тест успешного открытия изображения"""
        # Настройка моков
        test_file_path = "/fake/path/image.png"
        mock_get_open_file_name.return_value = (test_file_path, '')
        
        # Создаем реальный mock для MyImage с нужными методами
        mock_image_instance = Mock()
        mock_image_instance.get_scaled = Mock(return_value=Mock(spec=QPixmap))
        mock_my_image.return_value = mock_image_instance
        
        # Вызов тестируемого метода
        image_viewer._ImageViewer__open_image()
        
        # Проверки
        mock_get_open_file_name.assert_called_once()
        mock_my_image.assert_called_once_with(test_file_path)
        assert image_viewer.current_image == mock_image_instance
        assert image_viewer.save_action.isEnabled()
        assert image_viewer.zoom_in_btn.isEnabled()
        assert image_viewer.zoom_out_btn.isEnabled()
        assert image_viewer.original_size_btn.isEnabled()
        assert image_viewer.nav_up_btn.isEnabled()
        assert image_viewer.nav_down_btn.isEnabled()
        assert image_viewer.nav_left_btn.isEnabled()
        assert image_viewer.nav_right_btn.isEnabled()
        assert image_viewer.scale_factor == 1.0

    @patch('app.ui.QFileDialog.getOpenFileName')
    @patch('app.ui.MyImage')
    @patch('app.ui.QMessageBox.warning')
    def test_open_image_failure(self, mock_warning, mock_my_image, mock_get_open_file_name, image_viewer):
        """Тест неудачного открытия изображения"""
        # Настройка моков
        test_file_path = "/fake/path/image.png"
        mock_get_open_file_name.return_value = (test_file_path, '')
        mock_my_image.side_effect = Exception("Test error")
        
        # Вызов тестируемого метода
        image_viewer._ImageViewer__open_image()
        
        # Проверки
        mock_warning.assert_called_once()
        assert image_viewer.current_image is None

    def test_zoom_in(self, image_viewer):
        """Тест увеличения масштаба"""
        # Создаем mock для изображения с правильным возвращаемым типом
        image_viewer.current_image = Mock()
        image_viewer.current_image.get_scaled = Mock(return_value=Mock(spec=QPixmap))
        
        initial_scale = image_viewer.scale_factor
        
        # Мокаем метод отображения, чтобы избежать создания QPixmap
        with patch.object(image_viewer, '_ImageViewer__display_image') as mock_display:
            image_viewer._ImageViewer__zoom_in()
            
            # Проверяем, что масштаб изменился
            assert image_viewer.scale_factor == initial_scale * 1.25
            mock_display.assert_called_once()

    def test_zoom_in_max_limit(self, image_viewer):
        """Тест ограничения максимального масштаба"""
        image_viewer.current_image = Mock()
        image_viewer.scale_factor = 10.0
        
        with patch.object(image_viewer, '_ImageViewer__display_image') as mock_display:
            image_viewer._ImageViewer__zoom_in()
            
            # Проверяем, что масштаб не превысил максимум
            assert image_viewer.scale_factor == 10.0
            mock_display.assert_called_once()

    def test_zoom_out(self, image_viewer):
        """Тест уменьшения масштаба"""
        image_viewer.current_image = Mock()
        image_viewer.scale_factor = 2.0
        
        with patch.object(image_viewer, '_ImageViewer__display_image') as mock_display:
            image_viewer._ImageViewer__zoom_out()
            
            assert image_viewer.scale_factor == 2.0 * 0.8
            mock_display.assert_called_once()

    def test_zoom_out_min_limit(self, image_viewer):
        """Тест ограничения минимального масштаба"""
        image_viewer.current_image = Mock()
        image_viewer.scale_factor = 0.01
        
        with patch.object(image_viewer, '_ImageViewer__display_image') as mock_display:
            image_viewer._ImageViewer__zoom_out()
            
            # Проверяем, что масштаб не стал меньше минимума
            assert image_viewer.scale_factor == 0.01
            mock_display.assert_called_once()

    def test_original_size(self, image_viewer):
        """Тест сброса масштаба к оригинальному"""
        image_viewer.current_image = Mock()
        image_viewer.scale_factor = 2.5
        
        with patch.object(image_viewer, '_ImageViewer__display_image') as mock_display:
            image_viewer._ImageViewer__original_size()
            
            assert image_viewer.scale_factor == 1.0
            mock_display.assert_called_once()

    def test_navigation_buttons(self, image_viewer):
        """Тест кнопок навигации"""
        # Создаем реальные mock объекты для скроллбаров
        mock_h_scroll = Mock(spec=QScrollBar)
        mock_v_scroll = Mock(spec=QScrollBar)
        
        # Устанавливаем возвращаемые значения для value()
        mock_h_scroll.value.return_value = 100
        mock_v_scroll.value.return_value = 100
        
        # Мокаем методы scroll_area чтобы возвращали наши mock объекты
        image_viewer.scroll_area.horizontalScrollBar = Mock(return_value=mock_h_scroll)
        image_viewer.scroll_area.verticalScrollBar = Mock(return_value=mock_v_scroll)
        
        # Тестируем навигацию
        image_viewer._ImageViewer__nav_up()
        mock_v_scroll.setValue.assert_called_with(50)
        
        image_viewer._ImageViewer__nav_down()
        mock_v_scroll.setValue.assert_called_with(150)
        
        image_viewer._ImageViewer__nav_left()
        mock_h_scroll.setValue.assert_called_with(50)
        
        image_viewer._ImageViewer__nav_right()
        mock_h_scroll.setValue.assert_called_with(150)

    def test_mouse_events(self, image_viewer):
        """Тест обработки событий мыши"""
        # Создаем mock события для нажатия
        mock_press_event = Mock(spec=QMouseEvent)
        mock_press_event.button.return_value = Qt.MiddleButton
        mock_press_event.globalPos.return_value = QPoint(100, 100)
        
        # Тест нажатия средней кнопки мыши
        image_viewer._ImageViewer__mouse_press_event(mock_press_event)
        assert image_viewer.dragging == True
        assert image_viewer.last_mouse_pos == QPoint(100, 100)
        
        # Создаем mock события для перемещения
        mock_move_event = Mock(spec=QMouseEvent)
        mock_move_event.globalPos.return_value = QPoint(150, 150)
        
        # Мокаем скроллбары для теста перемещения
        mock_h_scroll = Mock(spec=QScrollBar)
        mock_v_scroll = Mock(spec=QScrollBar)
        mock_h_scroll.value.return_value = 100
        mock_v_scroll.value.return_value = 100
        
        image_viewer.scroll_area.horizontalScrollBar = Mock(return_value=mock_h_scroll)
        image_viewer.scroll_area.verticalScrollBar = Mock(return_value=mock_v_scroll)
        
        # Тест перемещения мыши
        image_viewer._ImageViewer__mouse_move_event(mock_move_event)
        
        # Проверяем, что скроллбары были обновлены
        mock_h_scroll.setValue.assert_called_with(100 - 50)  # 100 - (150-100)
        mock_v_scroll.setValue.assert_called_with(100 - 50)  # 100 - (150-100)
        
        # Создаем mock события для отпускания
        mock_release_event = Mock(spec=QMouseEvent)
        mock_release_event.button.return_value = Qt.MiddleButton
        
        # Тест отпускания кнопки мыши
        image_viewer._ImageViewer__mouse_release_event(mock_release_event)
        assert image_viewer.dragging == False
        assert image_viewer.last_mouse_pos is None

    def test_mouse_events_ignored(self, image_viewer):
        """Тест игнорирования событий мыши для других кнопок"""
        # Создаем mock события для левой кнопки мыши
        mock_event = Mock(spec=QMouseEvent)
        mock_event.button.return_value = Qt.LeftButton
        
        # Проверяем, что события игнорируются
        image_viewer._ImageViewer__mouse_press_event(mock_event)
        assert not image_viewer.dragging

    def test_display_image_with_current_image(self, image_viewer):
        """Тест отображения изображения когда current_image установлен"""
        # Создаем mock для изображения
        image_viewer.current_image = Mock()
        mock_qpixmap = Mock(spec=QPixmap)
        image_viewer.current_image.get_scaled.return_value = mock_qpixmap
        
        # Мокаем setPixmap для проверки вызова
        with patch.object(image_viewer.image_label, 'setPixmap') as mock_set_pixmap:
            image_viewer._ImageViewer__display_image()
            
            # Проверяем, что методы были вызваны с правильными аргументами
            image_viewer.current_image.get_scaled.assert_called_once_with(image_viewer.scale_factor)
            mock_set_pixmap.assert_called_once_with(mock_qpixmap)

    def test_display_image_without_current_image(self, image_viewer):
        """Тест отображения изображения когда current_image не установлен"""
        image_viewer.current_image = None
        
        # Мокаем setPixmap для проверки что он не вызывается
        with patch.object(image_viewer.image_label, 'setPixmap') as mock_set_pixmap:
            image_viewer._ImageViewer__display_image()
            
            # Проверяем, что setPixmap не был вызван
            mock_set_pixmap.assert_not_called()

    @patch('app.ui.QFileDialog.getSaveFileName')
    def test_save_image_no_current_image(self, mock_save_file_name, image_viewer):
        """Тест сохранения без текущего изображения"""
        image_viewer.current_image = None
        
        with patch('app.ui.QMessageBox.warning') as mock_warning:
            image_viewer._ImageViewer__save_image()
            
            mock_warning.assert_called_once_with(image_viewer, 'Ошибка', 'Нет изображения для сохранения')
            mock_save_file_name.assert_not_called()

    @patch('app.ui.QFileDialog.getSaveFileName')
    def test_save_image_cancel_dialog(self, mock_save_file_name, image_viewer):
        """Тест отмены диалога сохранения"""
        image_viewer.current_image = Mock()
        mock_save_file_name.return_value = ('', '')  # Пользователь отменил диалог
        
        with patch('app.ui.QMessageBox.information') as mock_info:
            image_viewer._ImageViewer__save_image()
            
            mock_info.assert_not_called()  # Сообщение об успехе не должно показываться

    @patch('app.ui.QFileDialog.getSaveFileName')
    def test_save_image_success(self, mock_save_file_name, image_viewer):
        """Тест успешного сохранения изображения"""
        # Настройка моков
        test_save_path = "/fake/path/saved_image.png"
        mock_save_file_name.return_value = (test_save_path, '')
        
        image_viewer.current_image = Mock()
        image_viewer.current_image.save = Mock()
        
        with patch('app.ui.QMessageBox.information') as mock_info:
            image_viewer._ImageViewer__save_image()
            
            # Проверяем, что методы были вызваны правильно
            image_viewer.current_image.save.assert_called_once_with(test_save_path)
            mock_info.assert_called_once()