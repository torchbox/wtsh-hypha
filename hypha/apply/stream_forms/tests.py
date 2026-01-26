from django.test import SimpleTestCase, TestCase
from faker import Faker

from .blocks import FormFieldBlock, FormFieldsBlock
from .validators import word_count

fake = Faker()


class TestBlocks(TestCase):
    def test_blocks_decode_none(self):
        for block in FormFieldsBlock().child_blocks.values():
            if isinstance(block, FormFieldBlock):
                with self.subTest(block=block):
                    value = block.decode(None)
                    self.assertIsNone(value)


class WordCountTestCase(SimpleTestCase):
    def test_word_count(self):
        testdata = [
            # text, expected word count
            ("lorem ipsum", 2),
            ("", 0),
            (" ", 0),
            ("lorem", 1),
            ("lorem ", 1),
        ]

        for text, expected_count in testdata:
            with self.subTest(text=text):
                self.assertEqual(
                    word_count(text),
                    expected_count,
                )
