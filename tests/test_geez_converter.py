import unittest
from kenat.geez_converter import to_geez, to_arabic
from kenat.exceptions import GeezConverterError

class TestGeezConverter(unittest.TestCase):

    # --- to_geez Tests ---
    def test_to_geez_single_digits(self):
        self.assertEqual(to_geez(1), '፩')
        self.assertEqual(to_geez(2), '፪')
        self.assertEqual(to_geez(9), '፱')

    def test_to_geez_tens(self):
        self.assertEqual(to_geez(10), '፲')
        self.assertEqual(to_geez(20), '፳')
        self.assertEqual(to_geez(99), '፺፱')

    def test_to_geez_hundreds(self):
        self.assertEqual(to_geez(100), '፻')
        self.assertEqual(to_geez(101), '፻፩')
        self.assertEqual(to_geez(110), '፻፲')
        self.assertEqual(to_geez(123), '፻፳፫')
        self.assertEqual(to_geez(999), '፱፻፺፱')

    def test_to_geez_thousands_and_ten_thousands(self):
        self.assertEqual(to_geez(1000), '፲፻')
        self.assertEqual(to_geez(10000), '፼')

    def test_to_geez_zero(self):
        self.assertEqual(to_geez(0), '0')

    def test_to_geez_string_input(self):
        self.assertEqual(to_geez('123'), '፻፳፫')
        self.assertEqual(to_geez('10000'), '፼')

    def test_to_geez_invalid_inputs(self):
        with self.assertRaises(GeezConverterError):
            to_geez(-1)
        with self.assertRaises(GeezConverterError):
            to_geez('abc')
        with self.assertRaises(GeezConverterError):
            to_geez(None)
        with self.assertRaises(GeezConverterError):
            to_geez(1.5)

    # --- to_arabic Tests ---
    def test_to_arabic_single_chars(self):
        self.assertEqual(to_arabic('፩'), 1)
        self.assertEqual(to_arabic('፪'), 2)
        self.assertEqual(to_arabic('፱'), 9)

    def test_to_arabic_tens(self):
        self.assertEqual(to_arabic('፲'), 10)
        self.assertEqual(to_arabic('፳'), 20)
        self.assertEqual(to_arabic('፺፱'), 99)

    def test_to_arabic_hundreds(self):
        self.assertEqual(to_arabic('፻'), 100)
        self.assertEqual(to_arabic('፻፩'), 101)
        self.assertEqual(to_arabic('፻፲'), 110)
        self.assertEqual(to_arabic('፻፳፫'), 123)
        self.assertEqual(to_arabic('፱፻፺፱'), 999)

    def test_to_arabic_thousands_and_ten_thousands(self):
        self.assertEqual(to_arabic('፲፻'), 1000)
        self.assertEqual(to_arabic('፼'), 10000)
        self.assertEqual(to_arabic('፲፼'), 100000)

    def test_to_arabic_complex(self):
        self.assertEqual(to_arabic('፲፻፺፱'), 1099)
        self.assertEqual(to_arabic('፬፻'), 400)

    def test_to_arabic_invalid_characters(self):
        with self.assertRaises(GeezConverterError):
            to_arabic('A')
        with self.assertRaises(GeezConverterError):
            to_arabic('፩X')

    def test_to_arabic_non_string_inputs(self):
        with self.assertRaises(GeezConverterError):
            to_arabic(None)
        with self.assertRaises(GeezConverterError):
            to_arabic(123)

    def test_round_trip_conversion(self):
        for n in [1, 10, 99, 100, 123, 999, 1000, 10000, 12345, 999999]:
            self.assertEqual(to_arabic(to_geez(n)), n)

if __name__ == '__main__':
    unittest.main()
