__author__ = 'sebastian'


class AnalyserEngine:
    def __init__(self, analyser_chain):
        self.analyser_chain = analyser_chain

    def process(self, analyser_table):
        for analyser in self.analyser_chain:
            self._process(analyser_table, analyser)

    def _process(self, analyser_table, analyser):
        if isinstance(analyser, list):
            for a in analyser:
                self._process(analyser_table, a)
        else:
            analyser.process(analyser_table)


class Analyser:
    def __init__(self):
        pass

    def process(self, analyser_table):
        pass


class AnalyserException(Exception):
    pass