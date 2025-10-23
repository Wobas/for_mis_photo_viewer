import pytest
import tempfile
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def temp_image_file():
    """Создает временное изображение для тестов"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        # Создаем простое изображение 100x100 пикселей
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.red)
        pixmap.save(tmp.name, "PNG")
        yield tmp.name
    # Удаляем временный файл после теста
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)

@pytest.fixture
def image_viewer(qapp):
    from app.ui import ImageViewer
    viewer = ImageViewer()
    yield viewer
    viewer.close()