__author__ = 'sebastian'


class DataTable:
    """
    A DataTable object represents a table plus some metadata.
    An instance should be closed using 'with' statement or close().
    'rows': Iterator over a list of messytables.cell objects. Use 'rows.sample' for a preview iterator.
    'headers': A list of strings containing the headers of the table. If none, there is no header.
    'types': A list of messytables.types objects.
    """
    def __init__(self, handle, headers=None, rows=None, types=None):
        self._handle = handle
        self.headers = headers
        self.rows = rows
        self.types = types

    def __repr__(self):
        return "DataTable (%s)" % self.types

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def close(self):
        self._handle.close()

    def register_processor(self, processor):
        """
        Register a stream processor to be used on each row.
        A processor is a object implementing the 'Processor' interface.
        """
        self.rows.register_processor(processor.visit)