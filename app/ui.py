import os
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout,
                            QFileDialog, QWidget, QLabel, QScrollArea,
                            QMessageBox, QAction, QGridLayout,  QPushButton)
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QPalette
from . import resources_rc
from .my_image import MyImage, ImageOpeningError, ImageSavingError

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUI()
        self.current_image: MyImage|None = None
        self.scale_factor = 1.0

        self.dragging = False
        self.last_mouse_pos = None
        self.scroll_position = None
        
    def __initUI(self):
        self.setWindowTitle('Просмотр изображений')
        self.setGeometry(100, 100, 800, 600)

        # Настройка верхней панели меню
        menubar = self.menuBar()

        # Раздел меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        # Пункт "Открыть"
        open_action = QAction('Открыть изображение', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Открыть изображение')
        open_action.triggered.connect(self.__open_image)
        file_menu.addAction(open_action)
        
        # Пункт "Сохранить"
        self.save_action = QAction('Сохранить изображение', self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.setStatusTip('Сохранить изображение')
        self.save_action.triggered.connect(self.__save_image)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)


        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной вертикальный layout, в котором хранятся кнопки управления и область просмотра изображений
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        main_layout.addLayout(toolbar_layout)

        # Область отображения изображения
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setBackgroundRole(QPalette.Dark)
        self.image_label.setMouseTracking(True) 
        self.image_label.mousePressEvent = self.__mouse_press_event
        self.image_label.mouseMoveEvent = self.__mouse_move_event
        self.image_label.mouseReleaseEvent = self.__mouse_release_event
        self.scroll_area.setWidget(self.image_label)
        main_layout.addWidget(self.scroll_area)

        self.overlay_widget = QWidget(self.scroll_area.viewport())
        zoom_layout = QVBoxLayout(self.overlay_widget)
        zoom_layout.setContentsMargins(5, 5, 5, 5)
        zoom_layout.setSpacing(5)
        
        # Кнопки масштабирования
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(QIcon(":/increase_loupe"))
        self.zoom_in_btn.clicked.connect(self.__zoom_in)
        self.zoom_in_btn.setEnabled(False)
        self.zoom_in_btn.setFixedSize(25, 25)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(QIcon(":/decrease_loupe"))
        self.zoom_out_btn.clicked.connect(self.__zoom_out)
        self.zoom_out_btn.setEnabled(False)
        self.zoom_out_btn.setFixedSize(25, 25)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        self.original_size_btn = QPushButton('x1')
        self.original_size_btn.clicked.connect(self.__original_size)
        self.original_size_btn.setEnabled(False)    
        self.original_size_btn.setFixedSize(25, 25)
        zoom_layout.addWidget(self.original_size_btn)

        # Кнопки навигации (панорамирования)
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(2)

        # Создаем контейнер для кнопок навигации в виде крестика
        nav_container = QWidget()
        nav_grid = QGridLayout(nav_container)
        nav_grid.setContentsMargins(0, 0, 0, 0)
        nav_grid.setSpacing(1)

        # Создаем кнопки навигации
        self.nav_up_btn = QPushButton('↑')
        self.nav_up_btn.setFixedSize(25, 25)
        self.nav_up_btn.clicked.connect(self.__nav_up)
        self.nav_up_btn.setEnabled(False)

        self.nav_down_btn = QPushButton('↓')
        self.nav_down_btn.setFixedSize(25, 25)
        self.nav_down_btn.clicked.connect(self.__nav_down)
        self.nav_down_btn.setEnabled(False)

        self.nav_left_btn = QPushButton('←')
        self.nav_left_btn.setFixedSize(25, 25)
        self.nav_left_btn.clicked.connect(self.__nav_left)
        self.nav_left_btn.setEnabled(False)

        self.nav_right_btn = QPushButton('→')
        self.nav_right_btn.setFixedSize(25, 25)
        self.nav_right_btn.clicked.connect(self.__nav_right)
        self.nav_right_btn.setEnabled(False)

        # Располагаем кнопки в виде крестика
        nav_grid.addWidget(self.nav_up_btn, 0, 1)
        nav_grid.addWidget(self.nav_left_btn, 1, 0)
        nav_grid.addWidget(self.nav_right_btn, 1, 2)
        nav_grid.addWidget(self.nav_down_btn, 2, 1)

        nav_layout.addWidget(nav_container)

        # Добавляем навигацию в основной layout панели инструментов
        zoom_layout.addLayout(nav_layout)

        # # Добавляем разделитель или отступ между группами кнопок
        # spacer = QWidget()
        # spacer.setFixedSize(10, 10)
        # zoom_layout.addWidget(spacer)

        # Статус
        self.statusBar().showMessage('Готов к работе')

    def __open_image(self):
        ''' Функция вызова окна открытия изображения '''
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Открыть изображение', 
            '', 
            'Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)'
        )
        
        if file_path:
            try:
                self.current_image = MyImage(file_path)
                self.__display_image()
                self.scale_factor = 1.0
                self.nav_up_btn.setEnabled(True)
                self.nav_down_btn.setEnabled(True)
                self.nav_left_btn.setEnabled(True)
                self.nav_right_btn.setEnabled(True)
                self.save_action.setEnabled(True)
                self.zoom_in_btn.setEnabled(True)
                self.zoom_out_btn.setEnabled(True)
                self.original_size_btn.setEnabled(True)
                self.statusBar().showMessage(f'Загружено: {os.path.basename(file_path)}')
                
            except ImageOpeningError as e:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить изображение')
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при загрузке изображения: {str(e)}')
    
    def __display_image(self):
        ''' Функция отрисовки изображения '''
        if self.current_image:
            self.image_label.setPixmap(QPixmap(self.current_image.get_scaled(self.scale_factor)))
    
    def __zoom_in(self):
        ''' Функция увеличения масштаба '''
        new_scale = self.scale_factor * 1.25
        if (new_scale > 10):
            self.scale_factor = 10
        else:
            self.scale_factor = new_scale
        self.__display_image()
        self.statusBar().showMessage(f'Масштаб: {self.scale_factor:.2f}x')
    
    def __zoom_out(self):
        ''' Функция уменьшения масштаба '''
        new_scale = self.scale_factor * 0.8
        if (new_scale < 0.01):
            self.scale_factor = 0.01
        else:
            self.scale_factor = new_scale
        self.__display_image()
        self.statusBar().showMessage(f'Масштаб: {self.scale_factor:.2f}x')
    
    def __original_size(self):
        ''' Функция сброса коэффициента масштаба '''
        self.scale_factor = 1.0
        self.__display_image()
        self.statusBar().showMessage('Оригинальный размер')
    
    def __save_image(self):
        ''' Функция вызова окна сохранения '''
        if not self.current_image:
            QMessageBox.warning(self, 'Ошибка', 'Нет изображения для сохранения')
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение как...", QDir.homePath(), "JPEG (*.jpg);;PNG (*.png);;BMP (*.bmp);;TIFF (*.tif)")
        if file_path:
            try:
                # Сохраняем оригинальное изображение, а не масштабированное
                self.current_image.save(file_path)
                QMessageBox.information(self, 'Успех', f'Изображение сохранено как {file_path}')
                self.statusBar().showMessage(f'Сохранено: {os.path.basename(file_path)}')
            except ImageSavingError as e:
                QMessageBox.warning(self, 'Ошибка', str(e))
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка при сохранении: {str(e)}')
        

    def __nav_up(self):
        """ Перемещение изображения вверх """
        v_scroll = self.scroll_area.verticalScrollBar()
        v_scroll.setValue(v_scroll.value() - 50)
        self.statusBar().showMessage('Перемещение вверх')

    def __nav_down(self):
        """ Перемещение изображения вниз """
        v_scroll = self.scroll_area.verticalScrollBar()
        v_scroll.setValue(v_scroll.value() + 50)
        self.statusBar().showMessage('Перемещение вниз')

    def __nav_left(self):
        """ Перемещение изображения влево """
        h_scroll = self.scroll_area.horizontalScrollBar()
        h_scroll.setValue(h_scroll.value() - 50)
        self.statusBar().showMessage('Перемещение влево')

    def __nav_right(self):
        """ Перемещение изображения вправо """
        h_scroll = self.scroll_area.horizontalScrollBar()
        h_scroll.setValue(h_scroll.value() + 50)
        self.statusBar().showMessage('Перемещение вправо')

    # Добавляем методы для обработки событий мыши
    def __mouse_press_event(self, ev: QMouseEvent):
        if ev.button() == Qt.MiddleButton:
            self.dragging = True
            self.last_mouse_pos = ev.globalPos()
            self.image_label.setCursor(Qt.ClosedHandCursor)
            ev.accept()
        else:
            ev.ignore()

    def __mouse_move_event(self, ev: QMouseEvent):
        if self.dragging and self.last_mouse_pos is not None:
            current_global_pos = ev.globalPos()
            delta = current_global_pos - self.last_mouse_pos
            self.last_mouse_pos = current_global_pos
            
            # Перемещаем скроллбары с учетом масштаба
            h_scroll = self.scroll_area.horizontalScrollBar()
            v_scroll = self.scroll_area.verticalScrollBar()
            h_scroll.setValue(h_scroll.value() - delta.x())
            v_scroll.setValue(v_scroll.value() - delta.y())
            ev.accept()
        else:
            ev.ignore()

    def __mouse_release_event(self, ev: QMouseEvent):
        if ev.button() == Qt.MiddleButton:
            self.dragging = False
            self.last_mouse_pos = None
            self.image_label.setCursor(Qt.ArrowCursor)
            ev.accept()
        else:
            ev.ignore()
