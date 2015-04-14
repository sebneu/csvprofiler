import logging
from analyser import Analyser
from alchemy_api import AlchemyApi

__author__ = 'sebastian'

logger = logging.getLogger(__name__)


def _api_lookup(row_string):
    logger.debug('alchemy api lookup on: ' + row_string)
    # Use alchemy api to detect entity, any other api can be implemented
    detector = EntityDetection(AlchemyApi())
    e = detector.guess_entity(row_string)
    logger.debug('detected entities: %s', e)
    return e


def _row_entity_detection(analyser_table):
    logger.debug('(%s) row entity analysis', analyser_table.name)
    row_labels = []
    for row in analyser_table.rows:
        row_string = ''
        for cell in row:
            if not cell.empty and cell.type.result_type == basestring:
                # split by . or _ or ,
                values = [cell.value]
                s = cell.value.split('.')
                if len(s) > 1:
                    values += s
                s = cell.value.split(',')
                if len(s) > 1:
                    values += s
                s = cell.value.split('_')
                if len(s) > 1:
                    values += s
                row_string += ' ' + ' '.join(values)

        e = _api_lookup(row_string)
        row_labels.append(e)
        print e


def _column_entity_detection(analyser_table):
    """
    Entity per column detection.
    Builds a string out of a column and hands it to an entity detection tool.


    :param analyser_table: the table
    :return:
    """
    logger.debug('(%s) column entity analysis', analyser_table.name)
    column_labels = []
    for column in analyser_table.columns:
        column_string = ''
        for cell in column:
            if not cell.empty and cell.type.result_type == basestring:
                # split by . or _ or ,
                # TODO split by capital letters, add header to analysis??
                values = [cell.value]
                s = cell.value.split('.')
                if len(s) > 1:
                    values += s
                s = cell.value.split(',')
                if len(s) > 1:
                    values += s
                s = cell.value.split('_')
                if len(s) > 1:
                    values += s
                column_string += ' ' + ' '.join(values)

        e = _api_lookup(column_string)
        column_labels.append(e)
        print 'column ' + cell.column
        for entity in e:
            print entity['type'], entity['text'], entity['count'], entity['relevance']
        print


class EntityAnalyser(Analyser):
    def process(self, analyser_table):
        # TODO do type analyser before this, to get rid of urls, mail, ids, non-words
        # _row_entity_detection(analyser_table)
        _column_entity_detection(analyser_table)


class EntityDetection:
    def __init__(self, detector):
        self.detector = detector

    def guess_entity(self, header):
        metadata = self.detector.entity(header)
        return metadata