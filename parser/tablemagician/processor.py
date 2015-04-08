import logging

__author__ = 'sebastian'


logger = logging.getLogger(__name__)


class Processor(object):
    def __init__(self, datatable):
        """
        Call this constructor in any child class constructor (if necessary):
        'super(ChildClass, self).__init__(datatable=datatable)'
        :param datatable: The constructor will register the processor to this datatable
        """
        self.datatable = datatable
        logger.debug('register custom processor: %s', self.__class__)
        self.datatable.register_processor(self)

    def visit(self, row_set, row):
        """
        :param row_set: the messytables-intern row_set object
        :param row: The current row
        :return: The (modified) row
        """
        return row

    def finalize(self):
        pass