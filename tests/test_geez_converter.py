# tests/test_geez_converter.py

import pytest
from kenat.geez_converter import toGeez, toArabic
from kenat.exceptions import GeezConverterError

class TestToGeez:
    """Tests the toGeez (Arabic to Ethiopic numeral) function."""

    def test_converts_single_digits(self):
        assert toGeez(1) == '፩'
        assert toGeez(2) == '፪'
        assert toGeez(9) == '፱'

    def test_converts_tens(self):
        assert toGeez(10) == '፲'
        assert toGeez(20) == '፳'
        assert toGeez(99) == '፺፱'

    def test_converts_hundreds(self):
        assert toGeez(100) == '፻'
        assert toGeez(101) == '፻፩'
        assert toGeez(256) == '፪፻፶፮'
        assert toGeez(999) == '፱፻፺፱'

    def test_converts_thousands(self):
        assert toGeez(1000) == '፲፻'
        assert toGeez(10000) == '፼'
        assert toGeez(12345) == '፼፳፫፻፵፭'

    def test_handles_large_numbers(self):
        assert toGeez(99999) == '፱፼፺፱፻፺፱'
        assert toGeez(100000) == '፲፼'

    def test_handles_zero(self):
        assert toGeez(0) == '0'

    def test_rejects_invalid_input(self):
        with pytest.raises(GeezConverterError, match="Input must be a non-negative integer."):
            toGeez(-5)
        with pytest.raises(GeezConverterError, match="Input must be a number or a string."):
            toGeez(1.5)
        with pytest.raises(GeezConverterError, match="Input must be a number or a string."):
            toGeez(None)


class TestToArabic:
    """Tests the toArabic (Ethiopic to Arabic numeral) function."""

    def test_converts_single_digits(self):
        assert toArabic('፩') == 1
        assert toArabic('፪') == 2
        assert toArabic('፱') == 9

    def test_converts_tens(self):
        assert toArabic('፲') == 10
        assert toArabic('፳') == 20
        assert toArabic('፺፱') == 99

    def test_converts_hundreds(self):
        assert toArabic('፻') == 100
        assert toArabic('፻፩') == 101
        assert toArabic('፪፻፶፮') == 256
        assert toArabic('፱፻፺፱') == 999

    def test_converts_ten_thousands(self):
        assert toArabic('፲፻') == 1000
        assert toArabic('፼') == 10000
        assert toArabic('፻፳፫፻፵፭') == 12345

    def test_handles_large_numbers(self):
        assert toArabic('፱፼፺፱፻፺፱') == 99999

    def test_rejects_invalid_geez_numeral(self):
        with pytest.raises(GeezConverterError, match="Unknown Ge'ez numeral: i"):
            toArabic('invalid')
        with pytest.raises(GeezConverterError, match="Invalid Ge'ez numeral sequence near ፩ in ፩፩"):
            toArabic('፩፩') # Repeated single digit
        with pytest.raises(GeezConverterError, match="Invalid Ge'ez numeral sequence near ፲ in ፲፲"):
            toArabic('፲፲') # Repeated tens
