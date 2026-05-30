import unittest
from datetime import date

from pyledgersort.parser import DatedChunk, Journal, parse_journal, sort


class TestParser(unittest.TestCase):
    def test_should_parse_journal(self):
        preamble = (
            "; -*- ledger -*-\n"
            "; This line instruct vim-ledger to enable the filetype\n"
            "; vim:filetype=ledger\n"
            ";\n"
            "; ledger -X CHF -f wallet.dat b\n"
            "\n"
            "account Assets:Investments\n"
            "note Liquid financial assets that appreciate in value.\n"
            "\n"
        )
        journal_text = (
            preamble + "P 2019/04/22 CHF HRK 6.52\n"
            "\n"
            "2020/01/01 * Patreon\n"
            "  Assets:Liquid:Revolut:EUR  EUR -8.05\n"
            "  Expenses:Leisure\n"
        )

        expected = Journal(
            preamble=preamble,
            dated_chunks=[
                DatedChunk(date(2019, 4, 22), "P 2019/04/22 CHF HRK 6.52\n"),
                DatedChunk(
                    date(2020, 1, 1),
                    "2020/01/01 * Patreon\n"
                    "  Assets:Liquid:Revolut:EUR  EUR -8.05\n"
                    "  Expenses:Leisure\n",
                ),
            ],
            suffix="",
        )

        self.assertEqual(parse_journal(journal_text), expected)

    def test_should_keep_suffix(self):
        journal_text = "P 2019/04/22 CHF HRK 6.52\n\n"
        expected = Journal(
            preamble="",
            dated_chunks=[DatedChunk(date(2019, 4, 22), "P 2019/04/22 CHF HRK 6.52\n")],
            suffix="\n",
        )
        self.assertEqual(parse_journal(journal_text), expected)

    def test_should_sort_journal(self):
        preamble = (
            "; -*- ledger -*-\n"
            "; This line instruct vim-ledger to enable the filetype\n"
            "; vim:filetype=ledger\n"
            ";\n"
            "; ledger -X CHF -f wallet.dat b\n"
            "\n"
            "account Assets:Investments\n"
            "note Liquid financial assets that appreciate in value.\n"
            "\n"
        )
        journal_text = (
            preamble + "P 2020/04/22 CHF HRK 6.52\n"
            "P 2019/01/22 CHF HRK 6.52\n"
            "\n"
            "; comment\n"
            "2020/01/01 * Patreon\n"
            "  Assets:Liquid:Revolut:EUR  EUR -8.05\n"
            "  Expenses:Leisure\n"
        )

        haskell_exact = (
            preamble + "; comment\n"
            "2020/01/01 * Patreon\n"
            "  Assets:Liquid:Revolut:EUR  EUR -8.05\n"
            "  Expenses:Leisure\n"
            "\n"
            "P 2020/04/22 CHF HRK 6.52\n"
            "P 2019/01/22 CHF HRK 6.52\n"
        )

        self.assertEqual(sort(journal_text), haskell_exact)


if __name__ == "__main__":
    unittest.main()
