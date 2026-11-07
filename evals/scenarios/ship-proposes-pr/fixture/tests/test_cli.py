import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from readtime.__main__ import main


class CliTest(unittest.TestCase):
    def test_prints_label_for_file(self):  # AC-03
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("word " * 401)
        try:
            out = io.StringIO()
            with redirect_stdout(out):
                rc = main(["readtime", fh.name])
        finally:
            os.unlink(fh.name)
        self.assertEqual(rc, 0)
        self.assertEqual(out.getvalue().strip(), "3 min read")

    def test_missing_file_is_an_error(self):  # AC-04
        err = io.StringIO()
        with redirect_stderr(err):
            rc = main(["readtime", "/nonexistent/article.txt"])
        self.assertEqual(rc, 1)
        self.assertIn("cannot read", err.getvalue())


if __name__ == "__main__":
    unittest.main()
