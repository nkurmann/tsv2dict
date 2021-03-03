'''
Provides a reader and writer for TSV files, similar to the CSV implementation.
'''
from inspect import signature
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import TextIO

__version__ = '0.0.2'


def escape(cell: Optional[str]) -> str:
    '''Make a string unambiguous when used in a tsv'''
    if cell is None:
        return r"\N"

    return (cell
            .replace("\\", r"\B")  # nonterminal symbol
            .replace("\n", r"\n")
            .replace("\r", r"\r")
            .replace("\t", r"\t")
            .replace(r"\B", "\\\\")
            )


def unescape(cell: str) -> Optional[str]:
    '''Deserialize a string from the tsv storage format'''

    if cell == r"\N":
        return None

    return (cell
            .replace(r"\\", r"\B")  # nonterminal symbol
            .replace(r"\n", "\n")
            .replace(r"\r", "\r")
            .replace(r"\t", "\t")
            .replace(r"\B", "\\")
            )


class Reader:
    '''Reads and unexcapes rows of tsv line by line.'''

    def __init__(self, f: Iterable[str]):
        self._file_it: Iterator[str] = iter(f)
        self._width = None

    def __iter__(self):
        return self

    def __next__(self) -> List[str]:
        '''Gets the next non-empty row of values.'''
        row: str = ""
        while not row:
            row = next(self._file_it).strip("\n").strip("\r")  # use removesuffix in 3.9

        assert "\n" not in row
        assert "\r" not in row
        values = row.split("\t")

        self._expect_number_of_cells_to_be_constant(len(values))

        return list(map(unescape, values))

    def _expect_number_of_cells_to_be_constant(self, width):
        '''Check that the file isn't ragged.'''
        if self._width is not None:
            if width is not self._width:
                raise ValueError("Cannot read rows with different widths.")
        else:
            self._width = width


class Writer:
    '''Writes rows into a tsv file. Performs escaping.'''

    def __init__(self, f: TextIO):
        self._file: TextIO = f
        self._width = None

    def write_row(self, cells: Iterable[Optional[str]]) -> None:
        '''Writes a single row into a tsv file. Performs escaping.'''
        self._expect_number_of_cells_to_be_constant(len(cells))

        escaped_cells = (escape(cell) for cell in cells)
        row = "\t".join(escaped_cells) + "\n"
        self._file.write(row)

    def _expect_number_of_cells_to_be_constant(self, width):
        '''Check that the file isn't ragged.'''
        if self._width is not None:
            if width is not self._width:
                raise ValueError("Cannot write rows with different widths.")
        else:
            self._width = width


class DictReader:
    '''Allows reading of tsv files in the form of dicts.'''

    def __init__(self,
                 f: Iterable[str],
                 fieldnames: Optional[List[str]] = None):
        """Allows reading of tsv files in the form of dicts.

        Args:
            f (Iterable[str]):
                The file to be read.
            fieldnames (List[str], optional):
                The keys to be assigned each row (and the resulting dict).
                If omitted, the keys are read from the first row.
        """
        self._reader: Reader = Reader(f)
        self.fieldnames: List[str] = fieldnames or next(self._reader)

    def __iter__(self):
        return self

    def __next__(self) -> Dict[str, str]:
        cells = next(self._reader)
        if len(cells) != len(self.fieldnames):
            raise ValueError(
                "The number of cells in the current line "
                "doesn't match the number of fieldnames. \n",
                {
                    "fieldnames": self.fieldnames,
                    "row": cells
                })
        return dict(zip(self.fieldnames, cells))


class DictWriter:
    '''Allows writing of dict values to a new or existing tsv file.'''

    def __init__(self,
                 f: TextIO,
                 write_header: bool,
                 fieldnames: Optional[Sequence[str]] = None,
                 missing_values_placeholder: Optional[str] = None,
                 allow_excess_values: bool = False):
        """Allows writing of dict values to a new or existing tsv file.

        Args:
            f (TextIO):
                The file to be written to.
            write_header (bool, optional):
                Whether the fieldnames should be written back to the file.
            fieldnames (Sequence[str], optional):
                The columns and their order.
                By default, they are inferred from the first dict passed.
            missing_values_placeholder (str, optional):
                Used when a dict is missing a value for a column.
                By default, throw a ValueException.
            allow_excess_values (bool, optional):
                Should dict entries without a column be discarded silently?
                By default, throw a KeyException.
        """
        self._expect_bool_type(write_header, "write_header")
        self._expect_bool_type(allow_excess_values, "allow_excess_values")
        self._writer = Writer(f)
        self._write_header = write_header
        self.fieldnames: Sequence[str] = fieldnames or None
        self.missing_values_placeholder: str = missing_values_placeholder
        self.allow_excess_values: bool = allow_excess_values

        if write_header and fieldnames is not None:
            self._writer.write_row(fieldnames)
            self._write_header = False

    @staticmethod
    def _expect_bool_type(value, name: str):
        if value not in (True, False):
            raise TypeError(f"{name} is expected to be a bool.")

    def write_row(self, rowdict: Dict[str, Any]) -> None:
        '''Writes a dict into the TSV as a single line'''

        if self.fieldnames is None:
            self.fieldnames = rowdict.keys()

        if self._write_header:
            self._writer.write_row(self.fieldnames)
            self._write_header = False

        row = self._build_row(rowdict)

        self._writer.write_row(row)

    def _build_row(self, rowdict: Dict[str, Any]) -> List[Optional[str]]:
        '''Constructs a row to match the file width'''

        if not self.allow_excess_values:
            self._expect_no_excess_values(rowdict)

        if self.missing_values_placeholder is None:
            self._expect_no_missing_values(rowdict)

        row: List[Optional[str]] = []
        for key in self.fieldnames:
            if key in rowdict:
                row.append(rowdict[key])
            else:
                row.append(self.missing_values_placeholder)
        return row

    def _expect_no_excess_values(self, rowdict):
        '''Throws an exception if values are not written back'''
        excess_values = set(rowdict.keys()) - set(self.fieldnames)
        if excess_values:
            raise KeyError(
                "These rowdict keys could not be written to the file: "
                + str(excess_values) + "\n"
                "Consider setting allow_excess_values in init."
            )

    def _expect_no_missing_values(self, rowdict):
        '''Throws an exception if values missing'''
        missing_values = set(self.fieldnames) - set(rowdict.keys())
        if missing_values:
            raise ValueError(
                "Rowdict is missing a value for rows: "
                + str(missing_values) + "\n"
                "Consider setting a missing_values_placeholder in init.")

    def write_rows(self, rowdicts: Iterable[Dict[str, Any]]):
        '''Adds several dicts in the form of as many rows'''
        for rowdict in rowdicts:
            self.write_row(rowdict)


def _expect_unary_function(type_: Callable[[str], Any]) -> bool:
    if len(signature(type_).parameters()) != 1:
        raise ValueError(f"Expected '{type_.__name__}' to be a unary function")


class ListConverter:
    '''An object that parses a list of strings into the types specified in `type_list`'''

    def __init__(self, type_list: List[Callable[[str], Any]]):
        if not all(map(callable, type_list)):
            raise TypeError("An entry in type_list isn't callable")

        self._type_list = type_list

    def __call__(self, row: List[str]) -> List[Any]:
        '''Cast the cells to the registered types'''
        if (len(self._type_list) != len(row)):
            raise ValueError("List length must match the number of predetermined types.")

        types_and_value = zip(self._type_list, row)
        return [target(value) for (target, value) in types_and_value]


class DictConverter:
    '''An object that parses a dict of strings into the types specified in `type_dict`'''

    def __init__(self, type_dict: Dict[str, Callable[[str], Any]]):
        if not all(map(callable, type_dict.values())):
            raise TypeError("An entry in type_dict isn't callable")

        self._target_types = type_dict

    def __call__(self, row_dict: Dict[str, str]) -> Dict[str, Any]:
        '''Cast the cells to the registered types'''
        if (len(self._target_types) != len(row_dict)):
            raise ValueError("Row length must match the number of predetermined types.")

        return {
            key: self._target_types[key](value) for (key, value) in row_dict.items()
        }
