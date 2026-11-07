"""CLI: python3 -m readtime <file> — prints the reading-time label for an article file."""

import sys

from readtime.core import label


def main(argv):
    if len(argv) != 2:
        print("usage: python3 -m readtime <file>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: cannot read {argv[1]}: {exc.strerror}", file=sys.stderr)
        return 1
    print(label(text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
