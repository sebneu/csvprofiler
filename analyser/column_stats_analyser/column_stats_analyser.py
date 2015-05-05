from analyser import Analyser, AnalyserException
from complex_type_analyser import ComplexTypeAnalyser
from complex_type_analyser.text import text_utils
import numpy as np

__author__ = 'sebastian'


class ColumnStatsAnalyser(Analyser):
    name = 'ColumnStatsAnalyser'

    def process(self, analyser_table):
        if ComplexTypeAnalyser.name not in analyser_table.analysers:
            raise AnalyserException(ComplexTypeAnalyser.name + ' required')
        compl_types = analyser_table.analysers[ComplexTypeAnalyser.name]

        stats = []
        for i, c in enumerate(analyser_table.columns):
            col_stats = {}
            col = np.array([cell.value for cell in c])
            unique_values, counts = np.unique(col, return_counts=True)

            # basic selectivity and distinct value stats
            col_stats['selectivity'] = len(unique_values)/float(len(col))
            col_stats['distinct'] = len(unique_values)

            # sort the unique values by their counts and store the top values
            sorted_values = [x for (y, x) in sorted(zip(counts, unique_values), reverse=True)]
            col_stats['top-5'] = sorted_values[:5]

            # count all rows which are numbers or floats in the current column of the complex type analyser
            num_types = sum(1 for t in compl_types[i] if t.startswith('NUMBER') or t.startswith('FLOAT'))
            total_types = len(compl_types)
            if 'EMPTY' in compl_types:
                total_types -= 1
            # check if all rows (except empty ones) are numbers or floats
            if total_types == num_types > 0:
                num_array = np.array([text_utils.parse_float(cell) for cell in col if not text_utils.is_none_type(str(cell).strip())])
                # collect descriptive stats
                col_stats['descriptive'] = {
                    'min': np.min(num_array),
                    'mean': np.mean(num_array),
                    'max': np.max(num_array),
                    'stddev': np.std(num_array),
                    'quartiles': [np.percentile(num_array, 25),
                                  np.percentile(num_array, 50),
                                  np.percentile(num_array, 75)]
                }
            stats.append(col_stats)

        analyser_table.analysers[ColumnStatsAnalyser.name] = stats