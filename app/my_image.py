import os
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class ImageOpeningError(Exception):
    pass

class ImageSavingError(Exception):
    pass

class MyImage:
    def __init__(self, file_path:str):
        self.__qimage = QImage(file_path)
        if self.__qimage.isNull():
            raise ImageOpeningError("Не удалось открыть изображение")
        
        self.__name = os.path.splitext(os.path.basename(file_path))[0]

    def save(self, file_path: str):
        ''' Функция сохранения изображения по указанному пути '''
        if not self.__qimage.save(file_path):
            raise ImageSavingError(f"Не удалось сохранить изображение '{self.__name}'")
    
    def get_width(self) -> int:
        ''' Метод получения ширины изображения '''
        return self.__qimage.width()
    
    def get_height(self) -> int:
        ''' Метод получения высоты изображения '''
        return self.__qimage.height()
    
    def get_scaled(self, scale: float) -> QImage:
        ''' Метод, создающий отмасштабированную компию изображения '''
        return self.__qimage.scaled(self.__qimage.size() * scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    def get_name(self) -> str:
        ''' Метод получеия имени изображения '''
        return self.__name
    