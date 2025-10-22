import os
from PyQt5.QtWidgets import (QHBoxLayout, QPushButton, QFileDialog, QMessageBox,
                            QComboBox, QLineEdit, QFormLayout, QDialog)

class SaveImageDialog(QDialog):
    def __init__(self, parent=None, file_name: str="image"):
        super().__init__(parent)
        self.__initUI(file_name)
        
    def __initUI(self, file_name):
        self.setWindowTitle('Сохранить изображение как')
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QFormLayout()
        self.setLayout(layout)
        
        # Выбор директории
        self.dir_edit = QLineEdit()
        self.dir_btn = QPushButton('Обзор...')
        self.dir_btn.clicked.connect(self.__select_directory)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.dir_btn)
        layout.addRow('Директория:', dir_layout)
        
        # Имя файла
        self.filename_edit = QLineEdit(file_name)
        layout.addRow('Имя файла:', self.filename_edit)
        
        # Тип файла
        self.format_combo = QComboBox()
        self.format_combo.addItems(['JPEG (*.jpg)', 'PNG (*.png)', 'BMP (*.bmp)', 'TIFF (*.tif)'])
        layout.addRow('Формат:', self.format_combo)
        
        # Кнопки подтверждения и отмены сохранения
        self.save_btn = QPushButton('Сохранить')
        self.save_btn.clicked.connect(self.__check_input)
        self.cancel_btn = QPushButton('Отмена')
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addRow(buttons_layout)
        
        
    def __select_directory(self):
        ''' Функция вызова контекстного окна выбора директории для сохранения '''
        directory = QFileDialog.getExistingDirectory(self, 'Выберите директорию')
        if directory:
            self.dir_edit.setText(directory)

    def __check_input(self):
        ''' Функция проверки введённых данных при подтверждении сохранения '''
        directory = self.dir_edit.text()
        filename = self.filename_edit.text()

        if not directory or not filename:
            QMessageBox.warning(self, 'Ошибка', 'Убедитесь, что заполнены поля "Директория" и "Имя файла"')
            return
        else:
            return self.accept()
    
    def get_save_info(self):
        directory = self.dir_edit.text()
        filename = self.filename_edit.text()
        format_text = self.format_combo.currentText()
        
        if not directory or not filename:
            return None, None
            
        # Определяем расширение файла из выбранного формата
        format_map = {
            'JPEG (*.jpg)': ('jpg', 'JPEG'),
            'PNG (*.png)': ('png', 'PNG'),
            'BMP (*.bmp)': ('bmp', 'BMP'),
            'TIFF (*.tif)': ('tif', 'TIFF')
        }
        
        extension, file_format = format_map[format_text]
        full_path = os.path.join(directory, f"{filename}.{extension}")
        
        return full_path, file_format