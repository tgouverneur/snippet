import json
from spx.spxsnippet import spxSnippet
from simplejson import JSONEncoder

class spxJSONEncoder(JSONEncoder):
    __types = ( spxSnippet )
    def default(self, obj):
        if isinstance(obj, spxJSONEncoder.__types):
            rs = obj.objToDict()
            return rs

        return json.JSONEncoder.default(self, obj)


