import pytest
import os
import pathlib
from PIL import Image

@pytest.fixture(scope="session", autouse=True)
def images_folder_location():
    return pathlib.Path("imgs")

@pytest.fixture(scope="session", autouse=True)
def images_subfolders(images_folder_location):
    return [i for i in images_folder_location.iterdir() if i.is_dir()]


def test_images_folder_exists(
    images_folder_location
):
    assert images_folder_location.exists()

def test_images_folder_is_not_empty(
    images_folder_location
):
    assert len(list(images_folder_location.iterdir())) > 0

def test_images_folder_contains_only_images(
    images_folder_location,
    images_subfolders
):
    for subfolder in images_subfolders:
        for file in subfolder.iterdir():
            assert file.suffix in [".jpg", ".png", ".jpeg"]

def test_images_are_not_empty(
    images_folder_location
    , images_subfolders
):
    for subfolder in images_subfolders:
        for file in subfolder.iterdir():
            assert file.stat().st_size > 0
    

def test_images_are_not_corrupted(
    images_folder_location,
    images_subfolders
):
    for subfolder in images_subfolders:
        for file in subfolder.iterdir():
            with Image.open(file) as img:
                img.verify()
    
def test_images_are_openable_by_pillow(
    images_folder_location,
    images_subfolders
):
    for subfolder in images_subfolders:
        for file in subfolder.iterdir():
            with Image.open(file) as img:
                img.load()