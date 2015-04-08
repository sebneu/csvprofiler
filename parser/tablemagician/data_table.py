import copy
import logging
from tablemagician.analyser_table import AnalyserTable

__author__ = 'sebastian'


logger = logging.getLogger(__name__)


class DataTable:
    """
    A DataTable object represents a table plus some metadata.
    An instance should be closed using 'with' statement or close().
    'headers': A list of strings containing the headers of the table. If none, there is no header.
    'types': A list of messytables.types objects.
    'filename': The local path or url
    """
    def __init__(self, handle, headers, rows, types, name, delimiter):
        # TODO mime_type, encoding
        self._handle = handle
        self.headers = headers
        self.types = types
        self.name = name
        self.delimiter = delimiter
        self._processors = []
        self._analysers = []
        self._rows = rows

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
        self._processors.append(processor)
        self._rows.register_processor(processor.visit)

    def get_processor(self, class_obj):
        for p in self._processors:
            if isinstance(p, class_obj):
                    return p
        return None

    def process(self, max_lines=-1):
        """

        :param max_lines: Optional, processes all lines on default.
        :return: A AnalyserTable object. Used for applying to analyser engine.
        """
        row_count = 0
        cols = [[] for _ in xrange(len(self.headers))]
        rows = []
        for r in self._rows:
            col_index = 0
            row = copy.deepcopy(r)
            rows.append(row)
            for c in row:
                cols[col_index].append(c)
                col_index += 1
            row_count += 1

            if 0 < max_lines <= row_count:
                break

        logger.debug('processed lines: %s', row_count)

        # finalize custom processors
        for p in self._processors:
            p.finalize()

        analyser_table = AnalyserTable(rows, cols, self.headers, self.types,
                                       self.name, self.delimiter)
        return analyser_table
