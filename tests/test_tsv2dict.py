from tsv2dict import DictReader
from tsv2dict import DictWriter
from tsv2dict import Reader
from tsv2dict import Writer
from tsv2dict import escape
from tsv2dict import unescape


class MockFile():
    def __init__(self):
        self.content: str = ""

    def write(self, s: str):
        self.content += s

    def readlines(self):
        return self.content.split('\n')


unescaped1 = "Harry\nAnd the chamber of pythons\r:"
escaped1 = r"Harry\nAnd the chamber of pythons\r:"
unescaped2 = "'\t' is escaped as '\\t'."
escaped2 = r"'\t' is escaped as '\\t'."


def test_escape():
    assert escape(unescaped1) == escaped1
    assert escape(unescaped2) == escaped2


def test_unescape():
    assert unescape(escaped1) == unescaped1
    assert unescape(escaped2) == unescaped2


test_tsv = [
    "Name\tAge\tAddress\n",
    "Me\t\tHere\n",
    "Jens\t5\t1234\\tVessy\n",
    "Jim\t23\tKreis 4\\nZürich\n",
    "\n",
    "The sun\t4'603'000'000\tn\\\\a\n",
]

test_header = ["Name", "Age", "Address"]
test_dicts = [
    {"Name": "Me", "Age": "", "Address": "Here"},
    {"Name": "Jens", "Age": "5", "Address": "1234\tVessy"},
    {"Name": "Jim", "Age": "23", "Address": "Kreis 4\nZürich"},
    {"Name": "The sun", "Age": "4'603'000'000", "Address": "n\\a"},
]
test_tsv_file = "tests/contacts.tsv"
test_tsv_lines = [test_header] + [list(d.values()) for d in test_dicts]


def test_reader():
    reader = Reader(test_tsv)
    actual = next(reader)
    assert actual == test_header


def test_reader_with_file():
    with open(test_tsv_file) as f:
        reader = Reader(f)
        for expected in test_tsv_lines:
            actual = next(reader)
            assert actual == expected


def test_reader_expects_equal_number_of_cells_per_line():
    f = ["a\tb\n",
         "1\t2\n",
         "1\t2\t3\n"]
    reader = Reader(f)
    next(reader)
    next(reader)
    try:
        next(reader)
        assert False
    except ValueError:
        assert True


def test_writer():
    f = MockFile()
    writer = Writer(f)
    writer.write_row(test_header)
    assert f.content == test_tsv[0]


def test_writer_expects_equal_number_of_cells_per_line():
    f = MockFile()
    writer = Writer(f)
    writer.write_row(["a", "b"])
    writer.write_row(["1", "2"])
    try:
        writer.write_row(["1", "2", "3"])
        assert False
    except ValueError:
        assert True


def test_dict_reader():
    reader = DictReader(test_tsv)
    assert reader.fieldnames == ["Name", "Age", "Address"]
    first = next(reader)
    assert first["Name"] == "Me"
    second = next(reader)
    assert second["Age"] == "5"
    third = next(reader)
    assert third["Address"] == "Kreis 4\nZürich"


def test_dict_reader_implements_iterable():
    dicts = [dict_ for dict_ in DictReader(test_tsv)]
    assert len(dicts) is len(test_dicts)


def test_dict_writer_with_write_header():
    f = MockFile()
    _ = DictWriter(f, True, ["A", "B", "C"])
    assert "A\tB\tC\n" == f.content


def test_values_are_written_in_the_same_order_as_the_header():
    f = MockFile()
    writer = DictWriter(f, False, ["B", "A", "C"])
    writer.write_row({"C": "c", "B": "2", "A": "1.00"})
    assert f.content == "2\t1.00\tc\n"


def test_writing_escapes_reserved_characters():
    f = MockFile()
    writer = DictWriter(f, False, ["B", "A", "C"])
    unescaped = "Harry\nAnd the chamber of pythons\\:"
    escaped = r"Harry\nAnd the chamber of pythons\\:"
    writer.write_row({"C": unescaped, "B": "2", "A": "1.00"})
    assert f"2\t1.00\t{escaped}\n" == f.content
