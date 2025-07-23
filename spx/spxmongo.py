from pymongo import MongoClient
from spx.spxexception import spxException

class spxMongo(object):

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            cls.__instance.__init()
        return cls.__instance

    _cols = {}

    def __init(self):
        self._mc = None
        self._db = None
        self._dbname = 'snippet'
        self._dbuser = None
        self._dbpass = None
        self._dbhost = 'localhost'
        self._dbport = 27017

    @staticmethod
    def registerCollection(collection, cls):
        spxMongo._cols[collection] = cls

    def setDBName(self, name):
        if self._mc:
            raise spxException('Connection is already done, disconnect before changing database name')

        self._dbname = name


    def setDBPort(self, port):
        if self._mc:
            raise spxException('Connection is already done, disconnect before changing database settings')

        self._dbport = port


    def setDBPassword(self, password):
        if self._mc:
            raise spxException('Connection is already done, disconnect before changing database settings')

        self._dbpass = password


    def setDBUsername(self, username):
        if self._mc:
            raise spxException('Connection is already done, disconnect before changing database settings')

        self._dbuser = username

    def setDBHost(self, host):
        if self._mc:
            raise spxException('Connection is already done, disconnect before changing database settings')

        self._dbhost = host

    def connect(self):
        if self._mc is not None:
            raise spxException('MongoDB is already connected, use disconnect() first')

        uri = 'mongodb://'
        if self._dbuser is not None:
            uri = uri + self._dbuser
            if self._dbpass is not None:
                uri = uri + ':' + self._dbpass
            uri = uri + '@'

        uri = uri + self._dbhost + ':' + str(self._dbport) + '/' + self._dbname

        self._mc = MongoClient(host=uri)
        self._db = self._mc[self._dbname]

    def disconnect(self):
        if not self._mc:
            raise spxException('MongoDB is not connected, cannot use disconnect()')

        self._mc.close()
        self._mc = None
        self._db = None

    def isConnected(self):
        if self._db is not None:
            return True
        return False

    def getDB(self):
        if self._db is None:
            raise spxException('getDB(): MongoDB is not connected')

        return self._db

    def getCollection(self, col):
        if self._db is None:
            raise spxException('getCollection(): MongoDB is not connected')

        return self._db[col]

    def getMongo(self):
        if self._mc is None:
            raise spxException('getMongo(): MongoDB is not connected')

        return self._mc

    def count(self, collection, f=None):
        return self.getCollection(collection).count(f)

    def findMany(self, cls=None, collection=None, where=None):
        where = {} if where is None else where

        if cls is None and collection is None:
            raise spxException('findMany(): need at least collection or cls')

        if collection is None:
            collection = cls._collection

        if cls is None:
            if collection not in spxMongo._cols:
                raise spxException('findMany(): cannot find collection in registered list')
            cls = spxMongo._cols[collection]

        rs = self.getCollection(collection).find(where)
        ret = []

        for i in rs:
            o = cls()
            o.setFromDB(i)
            ret.append(o)

        return ret




class spxMongoObject(object):

    ENOTFOUND = -1000

    def __init__(self):
        pass

    def _buildDoc(self, fs=None):
        doc = {}
        for o, m in type(self)._attrs.items():
            if fs:
                if o not in fs:
                    continue
            doc[m] = getattr(self, o)

        return doc

    def setFromDB(self, e):
        for o, m in type(self)._attrs.items():
            if m in e:
                setattr(self, o, e[m])

    def fetchFromField(self, f):
        self.fetchFromFields([f])

    def fetchFromFields(self, f):
        mc = spxMongo()
        e = mc.getCollection(type(self)._collection).find_one(self._buildDoc(f))
        if not e:
            raise spxException(rc=spxMongoObject.ENOTFOUND, msg='fetchFromFields(): Can\'t find entry in the database')
        self.setFromDB(e)

    def fetchFromId(self):
        mc = spxMongo()
        e = mc.getCollection(type(self)._collection).find_one(self._buildDoc(type(self)._attr_ids))
        if not e:
            raise spxException(rc=spxMongoObject.ENOTFOUND, msg='fetchFromId(): Can\'t find entry in the database')
        self.setFromDB(e)

    def save(self):
        mc = spxMongo()
        rs = mc.getCollection(type(self)._collection).replace_one(
                self._buildDoc(type(self)._attr_ids),
                self._buildDoc())
        if rs.matched_count < 1:
            raise spxException('replace_one() filter matched no objects')

    def insert(self):
        mc = spxMongo()
        mc.getCollection(type(self)._collection).insert_one(self._buildDoc())

    def find(self):
        pass

    def delete(self):
        mc = spxMongo()
        rs = mc.getCollection(type(self)._collection).delete_one(self._buildDoc(type(self)._attr_ids))
        if rs.deleted_count < 1:
            raise spxException('delete() filter matched no objects')

    def showMongo(self):
        print(type(self)._collection)

    def getCollection(self):
        return type(self)._collection


def getMongo():
    mc = spxMongo()

    if mc.isConnected():
        return mc

    mc.connect()
    return mc


