from bson.objectid import ObjectId
from spx.spxlogger import spxLogger
from spx.spxmongo import spxMongoObject, spxMongo
from spx.spxexception import spxException

class spxMetric(spxMongoObject):

    _collection = 'metrics'
    _attr_ids = ['id']
    _attrs = {
            'id': '_id',
            'name': 'name',
            'updated': 'updated',
            'created': 'created',
            }

    def __init__(self, id=None, name='', value=None):

        self.id = id
        if self.id is None:
            self.id = ObjectId()
        self.name = name
        self.value = value
        self.updated = None
        self.created = None
        if self.created is None:
            self.created = int(time.time())
        self.updated = self.created

    def __eq__(self, other):
        if self.name == other.name:
            return True
        return False

    def __ne__(self, other):
        if self.name != other.name:
            return True
        return False

    def __str__(self):
        return str(self.name)


    @staticmethod
    def updateMetric(name, value):
        pass

    @staticmethod
    def getMetric(name):
        pass

    @staticmethod
    def getAllMetrics():
        pass

