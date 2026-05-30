import sys

from pyledgersort.parser import ParseError, sort


def main():
    try:
        journal_text = sys.stdin.read()
        sorted_journal_text = sort(journal_text)
        sys.stdout.write(sorted_journal_text)
    except ParseError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
