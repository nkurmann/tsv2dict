from tsv2dict import DictConverter
from tsv2dict import DictReader
from tsv2dict import DictWriter
from tsv2dict import ListConverter
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
unescaped3 = None
escaped3 = r"\N"


def test_escape():
    assert escape(unescaped1) == escaped1
    assert escape(unescaped2) == escaped2
    assert escape(unescaped3) == escaped3


def test_unescape():
    assert unescape(escaped1) == unescaped1
    assert unescape(escaped2) == unescaped2
    assert unescape(escaped3) == unescaped3


test_tsv = [
    "Name\tAge\tAddress\n",
    "Me\t\tHere\n",
    "Jens\t5\t1234\\tVessy\n",
    "Jim\t23\tKreis 4\\nZürich\n",
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


def test_reader_ignores_empty_lines():
    reader = Reader(test_tsv[:3]+["\n"]+test_tsv[3:])
    actual = [dict_ for dict_ in reader]
    assert actual == test_tsv_lines


def test_reader_with_file():
    with open(test_tsv_file, encoding='UTF-8') as f:
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
    iterator = iter(DictReader(test_tsv))
    dicts = [dict_ for dict_ in iterator]
    assert len(dicts) is len(test_dicts)


def test_dict_writer_can_pass_header_explicityly():
    f = MockFile()
    _ = DictWriter(f, True, ["A", "B", "C"])
    assert f.content == "A\tB\tC\n"


def test_dict_writer_can_infer_header_from_dict():
    f = MockFile()
    writer = DictWriter(f, True, fieldnames=None)
    writer.write_rows(test_dicts)
    assert "".join(test_tsv) == f.content


def test_values_are_written_in_the_same_order_as_the_header():
    f = MockFile()
    writer = DictWriter(f, False, ["B", "A", "C"])
    writer.write_row({"C": "c", "B": "2", "A": "1.00"})
    assert f.content == "2\t1.00\tc\n"


def test_dict_writer_complains_when_missing_values():
    f = MockFile()
    writer = DictWriter(f, False, ["A", "B", "C"])
    try:
        writer.write_row({"B": "b", "C": "1.00"})
        assert False
    except ValueError:  # TODO: Is this the correct type of error?
        assert True


def test_dict_writer_can_use_missing_value_placeholder():
    f = MockFile()
    writer = DictWriter(f, False, ["A", "B", "C"], missing_values_placeholder="n/a")
    writer.write_row({"B": "b", "C": "1.00"})
    assert f.content == "n/a\tb\t1.00\n"


def test_dict_writer_complains_when_having_excess_values():
    f = MockFile()
    writer = DictWriter(f, False)
    try:
        rows = [{"A": "a", "B": "b", "C": "1.00"},
                {"A": "a", "B": "b", "C": "4.00", "X": "xx"}]
        writer.write_rows(rows)
        assert False
    except KeyError:  # TODO: Is this the correct type of error?
        assert True


def test_dict_writer_can_allow_excess_values():
    f = MockFile()
    writer = DictWriter(f, False, ["A", "B", "C"], allow_excess_values=True)
    writer.write_row({"A": "a", "B": "b", "C": "c", "X": "xx"})
    assert f.content == "a\tb\tc\n"


# def test_writing_escapes_reserved_characters():
#     f = MockFile()
#     writer = DictWriter(f, False, ["B", "A", "C"])
#     unescaped = "Harry\nAnd the chamber of pythons\\:"
#     escaped = r"Harry\nAnd the chamber of pythons\\:"
#     writer.write_row({"C": unescaped, "B": "2", "A": "1.00"})
#     assert f"2\t1.00\t{escaped}\n" == f.content

types_dict = {"A": str, "B": int, "C": float, "X": str, "Y": int, "Z": float}
types_list = [str, int, float, str, int, float]
data_list = ["a", "2", "3.0", None, None, None]
data_dict = {"A": "a", "B": "2", "C": "3.0", "X": None, "Y": None, "Z": None}
expected_list = ["a", 2, 3.0, None, None, None]
expected_dict = {"A": "a", "B": 2, "C": 3.0, "X": None, "Y": None, "Z": None}


def test_list_converter():
    converter = ListConverter(types_list)
    converted_list = converter(data_list)

    for actual, expected in zip(converted_list, expected_list):
        assert actual == expected
        assert isinstance(actual, type(expected))


def test_dict_converter():
    converter = DictConverter(types_dict)
    converted_dict = converter(data_dict)

    for key in converted_dict:
        assert converted_dict[key] == expected_dict[key]
        assert isinstance(converted_dict[key], type(expected_dict[key]))
