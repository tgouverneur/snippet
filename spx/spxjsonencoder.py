from spx.spxsnippet import spxSnippet
from json import JSONEncoder
import json

class spxJSONEncoder(JSONEncoder):
    __types = ( spxSnippet )
    def default(self, obj):
        if isinstance(obj, spxJSONEncoder.__types):
            rs = obj.objToDict()
            return rs

        return json.JSONEncoder.default(self, obj)


