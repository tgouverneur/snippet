import os
import sys
import pytest

# Add repository root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from spx.spxsnippet import spxSnippet
from spx.spxmongo import spxMongo


class DummyCollection:
    def __init__(self):
        self.counter = 0

    def find(self, where):
        # mutate incoming where to simulate side effects
        where['count'] = where.get('count', 0) + 1
        self.counter += 1
        return [{'v': where['count']}]


class DummyObj:
    _collection = 'dummy'

    def __init__(self):
        self.data = None

    def setFromDB(self, record):
        self.data = record


def test_encrypt_decrypt():
    original_content = 'hello world'
    original_email = 'user@example.com'
    original_reference = 'ref123'

    snip = spxSnippet(content=original_content)
    snip.email = original_email
    snip.reference = original_reference

    snip.encrypt()
    key = snip.clearKey

    # after encryption content should not equal original and be bytes
    assert snip.content != original_content
    assert isinstance(snip.content, (bytes, bytearray))

    assert snip.decrypt(key) is True

    assert snip.content == original_content
    assert snip.email == original_email
    assert snip.reference == original_reference

def test_findMany_repeated(monkeypatch):
    mc = spxMongo()
    dummy_collection = DummyCollection()

    monkeypatch.setattr(mc, 'getCollection', lambda name: dummy_collection)

    first = mc.findMany(cls=DummyObj)
    second = mc.findMany(cls=DummyObj)

    assert len(first) == 1
    assert first[0].data == {'v': 1}

    assert len(second) == 1
    assert second[0].data == {'v': 1}

