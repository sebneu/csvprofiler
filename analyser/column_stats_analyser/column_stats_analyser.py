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
            num_types = sum(1 for t in compl_types[i] if t.startswith('NUMBER'))
            total_types = len(compl_types[i])
            if 'EMPTY' in compl_types[i]:
                total_types -= 1            # check if all rows (except empty ones) are numbers or floats
            if total_types == num_types > 0:
                num_array = np.array([text_utils.parse_float(cell) for cell in col if not text_utils.is_none_type(str(cell).strip())])
                # collect descriptive stats
                col_stats['descriptive'] = _descriptive_analysis(num_array)
                # monotonic in/decreasing
                reg = _regression_analysis(num_array)
                if reg:
                    col_stats['regression'] = reg
            stats.append(col_stats)

        analyser_table.analysers[ColumnStatsAnalyser.name] = stats


def _descriptive_analysis(num_array):
    return {
        'min': np.min(num_array),
        'mean': np.mean(num_array),
        'max': np.max(num_array),
        'stddev': np.std(num_array),
        'quartiles': [np.percentile(num_array, 25),
                      np.percentile(num_array, 50),
                      np.percentile(num_array, 75)]
    }


def _regression_analysis(num_array):
    # different types of in, and decrease:
    # LINEAR -> steps
    # MONOTONIC -> (with errors?)
    linear = True
    prev_i = None
    prev_step = None
    step = 0
    is_incr = True
    is_decr = True
    for i in num_array:
        if prev_i:
            step = i - prev_i
        # check if the steps are linear, i.e. the previous step is the same as this one
        if prev_step:
            if linear and prev_step != step:
                linear = False
        # check the numbers are increasing
        if is_incr and step < 0:
            is_incr = False
        # check the numbers are decreasing
        if is_decr and step > 0:
            is_decr = False

        prev_i = i
        prev_step = step
    if linear:
        if is_incr:
            return 'INCREASE/LINEAR/' + str(step)
        if is_decr:
            return 'DECREASE/LINEAR/' + str(step)
    if is_incr:
        return 'INCREASE/MONOTONIC'
    if is_decr:
        return 'DECREASE/MONOTONIC'
    return None


