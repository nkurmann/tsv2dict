=====
Usage
=====


This project provides a `DictReader` and `DictWriter` for [linear TSV](http://dataprotocols.org/linear-tsv/) files, inspired by the ones available in `csv.py`.

To use tsv2dict in a project::

	$ pip install tsv2dict


The file's header can automatically be interpreted as fieldnames::

	from tsv2dict import DictReader, DictWriter

	# load and infer keys from header:
	with open(tsv_path, encoding="UTF-8") as f:
		rows = [row for row in DictReader(f)]

	# save and write keys to header:
	with open(tsv_path, 'w') as f:
		DictWriter(f, write_header=True).write_rows(rows)


If you're using a pure (headerless) linear tsv file, use::

	from tsv2dict import DictReader, DictWriter
	
	fieldnames = ["name", "age", "address"]

	# load (infer keys from header):
	with open(tsv_path, encoding="UTF-8") as f:
		rows = [row for row in DictReader(f, fieldnames)]

	# save (write keys to header):
	with open(tsv_path, 'w') as f:
		DictWriter(f, write_header=False, fieldnames).write_rows(rows)







> **Note:** If your TSV files originate in excel and contains quotes, tabs, or newlines, you might be better served using `csv.py`'s implementation with [excel_tab](https://docs.python.org/3/library/csv.html#csv.excel_tab), or `pandas`.
