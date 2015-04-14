from alchemyapi.alchemyapi import AlchemyAPI

__author__ = 'sebastian'


class AlchemyApi:
    def __init__(self):
        self.alchemyapi = AlchemyAPI()

    def entity(self, text):
        response = self.alchemyapi.entities("text", text)
        return response['entities']

    def concept(self, text):
        response = self.alchemyapi.concepts("text", text)
        return response
