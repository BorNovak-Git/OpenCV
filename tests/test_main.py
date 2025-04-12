# tests/test_main.py
import cv2

def test_cv_version():
    assert cv2.__version__ is not None
