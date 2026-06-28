import math
import os.path
from unittest.mock import patch

import httpretty
import pytest


from PyQt6 import QtCore, QtGui

from beeref.fileio.image import load_image


@pytest.mark.parametrize('path,expected',
                         [('test3x3.png', 'test3x3.png'),
                          ('test3x3_orientation1.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation2.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation3.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation4.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation5.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation6.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation7.jpg', 'test3x3.jpg'),
                          ('test3x3_orientation8.jpg', 'test3x3.jpg')])

def test_load_image_loads_from_filename(view, imgfilename3x3):
    img, filename = load_image(imgfilename3x3)
    assert img.isNull() is False
    assert filename == imgfilename3x3


def test_load_image_loads_from_nonexisting_filename(view, imgfilename3x3):
    img, filename = load_image('foo.png')
    assert img.isNull() is True
    assert filename == 'foo.png'


def test_load_image_loads_from_existing_local_url(view, imgfilename3x3):
    url = QtCore.QUrl.fromLocalFile(imgfilename3x3)
    img, filename = load_image(url)
    assert img.isNull() is False
    assert filename == imgfilename3x3


@httpretty.activate
def test_load_image_loads_from_existing_web_url(view, imgdata3x3):
    url = 'http://example.com/foo.png'
    httpretty.register_uri(
        httpretty.GET,
        url,
        body=imgdata3x3,
    )
    img, filename = load_image(QtCore.QUrl(url))
    assert img.isNull() is False
    assert filename == url


@httpretty.activate
def test_load_image_loads_from_existing_web_url_non_ascii(view, imgdata3x3):
    url = 'http://example.com/föö.png'
    httpretty.register_uri(
        httpretty.GET,
        url,
        body=imgdata3x3,
    )
    img, filename = load_image(QtCore.QUrl(url))
    assert img.isNull() is False
    assert filename == 'http://example.com/f%C3%B6%C3%B6.png'


@httpretty.activate
def test_load_image_loads_from_web_url_errors(view, imgfilename3x3):
    url = 'http://example.com/foo.png'
    httpretty.register_uri(
        httpretty.GET,
        url,
        status=500,
    )
    img, filename = load_image(QtCore.QUrl(url))
    assert img.isNull() is True
    assert filename == url


@httpretty.activate
def test_load_image_from_pinterest_finds_image(view, imgdata3x3):
    url = 'http://pinterest.com/a1b2c3/'
    img_url = 'http://pinterest.com/foo.png'
    httpretty.register_uri(
        httpretty.GET,
        url,
        body=f'<html><body><img src="{img_url}"/></body></html>',
    )
    httpretty.register_uri(
        httpretty.GET,
        img_url,
        body=imgdata3x3,
    )
    img, filename = load_image(QtCore.QUrl(url))
    assert img.isNull() is False
    assert filename == img_url


@httpretty.activate
def test_load_image_from_pinterest_when_already_image(view, imgdata3x3):
    img_url = 'http://pinterest.com/foo.png'
    httpretty.register_uri(
        httpretty.GET,
        img_url,
        body=imgdata3x3,
    )
    img, filename = load_image(QtCore.QUrl(img_url))
    assert img.isNull() is False
    assert filename == img_url


@httpretty.activate
def test_load_image_from_pinterest_when_img_url_not_found(view, imgdata3x3):
    url = 'http://pinterest.com/a1b2c3/'
    img_url = 'http://pinterest.com/foo.png'
    httpretty.register_uri(
        httpretty.GET,
        url,
        body='<html><body><p>no image here</p></body></html>',
    )
    httpretty.register_uri(
        httpretty.GET,
        img_url,
        body=imgdata3x3,
    )
    img, filename = load_image(QtCore.QUrl(url))
    assert img.isNull() is True


@httpretty.activate
def test_load_image_from_pinterest_when_url_errors(view, imgdata3x3):
    url = 'http://pinterest.com/a1b2c3/'
    httpretty.register_uri(
        httpretty.GET,
        url,
        status=500,
    )
    img, filename = load_image(QtCore.QUrl(url))
    assert img.isNull() is True
