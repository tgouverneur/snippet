import os
import sys

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
import spx.spxflask as spxflask
import spx.spxsnippet as spxsnippet
import spx.spxjsonencoder as spxjsonencoder

class DummySnippet:
    def __init__(self, id=None, created=0):
        self.id = id
        self.isConfirm = False
        self.content = ''
        self.name = ''
        self.isRaw = False
        self.isFile = False
        self.created = created
    def fetchFromId(self):
        pass
    def decrypt(self, key):
        return True
    def delete(self):
        pass
    def objToDict(self):
        return {
            'id': str(self.id),
            'content': self.content,
            'created': self.created,
            'isRaw': self.isRaw,
            'isFile': self.isFile,
            'name': self.name,
        }


def setup_patches(monkeypatch, mongo_obj):
    monkeypatch.setattr(spxflask, 'getMongo', lambda: mongo_obj)
    monkeypatch.setattr(spxflask, 'spxSnippet', DummySnippet)
    monkeypatch.setattr(spxsnippet, 'spxSnippet', DummySnippet)
    monkeypatch.setattr(spxjsonencoder, 'spxSnippet', DummySnippet)
    monkeypatch.setattr(spxjsonencoder.spxJSONEncoder, '_spxJSONEncoder__types', (DummySnippet,))
    monkeypatch.setattr(spxflask, 'ObjectId', lambda x: x)


def test_snippet_handler_disconnect(monkeypatch):
    called = {'d': False}
    class DummyMongo:
        def disconnect(self):
            called['d'] = True
    setup_patches(monkeypatch, DummyMongo())

    app = Flask(__name__)
    app.config['FORWARDFOR'] = 'False'
    spxflask.spxSnippetHandler.app = app

    with app.test_request_context('/'):
        spxflask.spxSnippetHandler().get(uid='1'*24, key='k'*32)
    assert called['d'] is True


def test_clean_handler_disconnect(monkeypatch):
    called = {'d': False}
    class DummyMongo:
        def findMany(self, cls=None, collection=None, where=None):
            return [DummySnippet(created=0)]
        def disconnect(self):
            called['d'] = True
    setup_patches(monkeypatch, DummyMongo())

    app = Flask(__name__)
    app.config['FORWARDFOR'] = 'False'
    app.config['SECRET_KEY'] = 'pw'
    spxflask.spxSnippetHandler.app = app
    spxflask.spxCleanHandler.app = app

    with app.test_request_context('/'):
        spxflask.spxCleanHandler().get(password='pw')
    assert called['d'] is True
