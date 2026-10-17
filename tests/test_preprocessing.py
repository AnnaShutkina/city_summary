import unittest

from processing.preprocessing import (
    DEFAULT_DESCRIPTION,
    is_expensive,
    needs_warm_clothes,
    normalize_description,
    preprocess_rate,
    preprocess_weather,
)


class PreprocessingTests(unittest.TestCase):
    def test_warm_clothes_when_below_zero(self) -> None:
        self.assertTrue(needs_warm_clothes(-3.2))
        self.assertFalse(needs_warm_clothes(0))
        self.assertFalse(needs_warm_clothes(15.5))

    def test_expensive_when_rate_above_100(self) -> None:
        self.assertTrue(is_expensive(100.01))
        self.assertFalse(is_expensive(100))
        self.assertFalse(is_expensive(92.15))

    def test_empty_description_gets_default(self) -> None:
        self.assertEqual(normalize_description(""), DEFAULT_DESCRIPTION)
        self.assertEqual(normalize_description("   "), DEFAULT_DESCRIPTION)
        self.assertEqual(normalize_description(None), DEFAULT_DESCRIPTION)
        self.assertEqual(normalize_description("clear sky"), "clear sky")

    def test_preprocess_weather_adds_flag(self) -> None:
        result = preprocess_weather({"temp_c": -3.2, "description": "clear sky"})
        self.assertEqual(
            result,
            {"temp_c": -3.2, "description": "clear sky", "warm_clothes": True},
        )

    def test_preprocess_rate_adds_flag(self) -> None:
        result = preprocess_rate("USD", 92.15)
        self.assertEqual(
            result,
            {"currency": "USD", "rate_to_rub": 92.15, "expensive": False},
        )


if __name__ == "__main__":
    unittest.main()
