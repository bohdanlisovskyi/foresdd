import unittest

from readtime.core import WORDS_PER_MINUTE, label, minutes, word_count


class WordCountTest(unittest.TestCase):
    def test_splits_on_any_whitespace(self):
        self.assertEqual(word_count("one  two\nthree\tfour"), 4)


class MinutesTest(unittest.TestCase):
    def test_exact_multiple(self):  # AC-01
        self.assertEqual(minutes("w " * (WORDS_PER_MINUTE * 2)), 2)

    def test_rounds_partial_minute_up(self):  # AC-01
        self.assertEqual(minutes("w " * (WORDS_PER_MINUTE + 1)), 2)

    def test_empty_text_is_zero(self):  # AC-02
        self.assertEqual(minutes(""), 0)
        self.assertEqual(minutes("   \n "), 0)


class LabelTest(unittest.TestCase):
    def test_label_in_minutes(self):  # AC-03
        self.assertEqual(label("w " * 450), "3 min read")

    def test_label_for_empty_text(self):  # AC-02
        self.assertEqual(label(""), "under a minute")


if __name__ == "__main__":
    unittest.main()
