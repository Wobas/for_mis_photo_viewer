import pytest
from app.my_image import ImageOpeningError, ImageSavingError, MyImage

def test_opening_invalid():
    with pytest.raises(ImageOpeningError):
        image = MyImage("wrong_file_path")
    
def test_opening_valid():
    image = MyImage("./tests/test_data/image.png")
    assert image.get_name() == "image"

def test_saving_invalid():
    with pytest.raises(ImageSavingError):
        image = MyImage("./tests/test_data/image.png")
        image.save("./invalid_path/")

def test_saving_valid():
    image = MyImage("./tests/test_data/image.png")
    image.save("./save_test_imgs_dir/test_image.jpg")
    image = MyImage("./save_test_imgs_dir/test_image.jpg")
