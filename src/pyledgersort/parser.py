import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import List

import parsy  # type: ignore
from parsy import eof, regex, string


@dataclass
class DatedChunk:
    date: date
    content: str


@dataclass
class Journal:
    preamble: str
    dated_chunks: List[DatedChunk]
    suffix: str


class ParseError(Exception):
    pass


def parse_date(date_str: str) -> date:
    if "-" in date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        return datetime.strptime(date_str, "%Y/%m/%d").date()


emptyLine = string("\n")

# nonEmptyLine: at least one character that is not a newline, followed by newline or EOF
nonEmptyLine = regex(r"[^\n]+(?:\n|$)")

# commentLine: starts with ';', followed by anything except newline, then newline or EOF
commentLine = regex(r";[^\n]*(?:\n|$)")

# datedLine: optional 'P ' followed by date, followed by anything except newline, then newline or EOF
datedLineStr = regex(r"(?:P[ \t]+)?\d{4}[-/]\d{1,2}[-/]\d{1,2}[^\n]*(?:\n|$)")


@parsy.generate
def datedLineWithStr():
    line = yield datedLineStr
    m = re.search(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}", line)
    if m:
        day = parse_date(m.group(0))
        return (line, day)
    # Should not reach here because datedLineStr regex guarantees a match
    yield parsy.fail("Invalid date string")


@parsy.generate
def datedChunkStart():
    yield emptyLine.many()
    comments = yield commentLine.many()
    line, day = yield datedLineWithStr
    return ("".join(comments), line, day)


@parsy.generate
def datedChunk():
    comments_str, dated_line_str, day = yield datedChunkStart
    nels = yield nonEmptyLine.many()
    return DatedChunk(day, comments_str + dated_line_str + "".join(nels))


@parsy.generate
def undatedChunk():
    yield datedChunkStart.should_fail("expected undated line")
    lines = yield nonEmptyLine.at_least(1)
    return "".join(lines)


undatedChunksOrEmptyLines = emptyLine | undatedChunk


@parsy.generate
def preamble():
    chunks = yield undatedChunksOrEmptyLines.many()
    return "".join(chunks)


@parsy.generate
def journalParser():
    preamble_text = yield preamble
    dated_chunks = yield datedChunk.many()
    suffix_newlines = yield emptyLine.many()
    yield eof
    return Journal(preamble_text, dated_chunks, "".join(suffix_newlines))


def parse_journal(text: str) -> Journal:
    try:
        return journalParser.parse(text)
    except parsy.ParseError as e:
        raise ParseError(str(e))


def sort_journal(journal: Journal) -> Journal:
    sorted_chunks = sorted(journal.dated_chunks, key=lambda c: c.date)
    return Journal(journal.preamble, sorted_chunks, journal.suffix)


def show_journal(journal: Journal) -> str:
    chunks_str = "\n".join(c.content for c in journal.dated_chunks)
    return journal.preamble + chunks_str + journal.suffix


def sort(text: str) -> str:
    journal = parse_journal(text)
    sorted_journal = sort_journal(journal)
    return show_journal(sorted_journal)
