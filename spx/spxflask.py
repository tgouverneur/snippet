from flask import Flask
from flask import Response
from flask import abort
from flask import request
from flask import g
from flask.views import MethodView
from functools import wraps

import base64
import socket
import time
import json
from datetime import date

from bson.objectid import ObjectId
from bson.objectid import InvalidId

from spx.spxmongo import spxMongo, spxMongoObject, getMongo
from spx.spxsnippet import spxSnippet
from spx.spxjsonencoder import spxJSONEncoder
from spx.spxlogger import spxLogger
from spx.spxexception import spxException


class spxSnippetHandler(MethodView):
    decorators = []

    def post(self):
        ret = None
        if not request.data:
            spxLogger.logAction('ADD_SNIP', request.remote_addr, 'FAIL')
            return Response(json.dumps({'rc': -1, 'error': 'No JSON data provided'}), 200, [('Content-Type', 'application/json')])

        mc = getMongo()

        p = json.loads(request.data.decode('utf-8'))

        if not p:
            spxLogger.logAction('ADD_SNIP', request.remote_addr, 'FAIL')
            return Response(json.dumps({'rc': -1, 'error': 'Provided data could not be loaded'}), 200, [('Content-Type', 'application/json')])

        p['createdBy'] = str(request.remote_addr)
        sp = spxSnippet()
        try:
            sp.dictToObj(p)

            if sp.isFile:
                sp.stripFile()
            else:
                sp.isRaw = False
                sp.stripXSS()

            sp.encrypt()
        except spxException as e:
            ret = {'rc': e.rc, 'error': e.msg}
            spxLogger.logAction('ADD_SNIP', request.remote_addr, 'FAIL', obj=e)
        except Exception as e:
            ret = {'rc': -2, 'error': 'Error creating the snippet: '+str(e)}
            spxLogger.logAction('ADD_SNIP', request.remote_addr, 'FAIL', obj=e)

        if ret is not None:
            return Response(json.dumps(ret), 200, [('Content-Type', 'application/json')])

        try:
            sp.insert()
            ret = {}
            ret['rc'] = 0
            ret['msg'] = 'The snippet has been added into the database'
            ret['key'] = sp.clearKey
            ret['id'] = str(sp.id)
        except spxException as e:
            ret = {'rc': e.rc, 'error': e.msg}
            spxLogger.logAction('ADD_SNIP', request.remote_addr, 'FAIL', obj=e)
            return Response(json.dumps(ret), 200, [('Content-Type', 'application/json')])
        except Exception as e:
            ret = {'rc': -2, 'error': 'Error adding the snippet into database: '+str(e)}
            spxLogger.logAction('ADD_SNIP', request.remote_addr, 'FAIL', obj=e)
            return Response(json.dumps(ret), 200, [('Content-Type', 'application/json')])

        spxLogger.logAction('ADD_SNIP', request.remote_addr, 'ALLOW', obj=sp)
        mc.disconnect()

        return Response(json.dumps(ret), 200, [('Content-Type', 'application/json')])


    def get(self, uid=None, key=None):
        ret = {}

        if uid is None or key is None:
            spxLogger.logAction('GET_SNIP', request.remote_addr, 'DENY')
            return Response(json.dumps({'rc': -1, 'error': 'You are not authorized to use this function'}), 403, [('Content-Type', 'application/json')])

        mc = getMongo()

        try:
            snip = spxSnippet(id=ObjectId(uid))
            snip.fetchFromId()
            if not snip.decrypt(key):
                raise spxException(rc=-1, msg='Decryption failed, please check your key')

            if snip.isConfirm:
                snip.sendConfirmation(spxSnippetHandler.app.config['SMTP_SERVER'], spxSnippetHandler.app.config['MAIL_FROM'], remote_addr=request.remote_addr)

            ret = snip
            """ remove the snippet """
            snip.delete()
            spxLogger.logAction('GET_SNIP', request.remote_addr, 'ALLOW', obj=uid)
        except spxException as e:
            spxLogger.logAction('GET_SNIP', request.remote_addr, 'FAIL', obj=e)
            ret = {'rc': e.rc, 'error': 'Sorry, the snippet you are trying to retrieve does not exist or was already accessed. Please contact the person who sent you the secure snippet so they can re-create the snippet and send you a new link.'}
        except InvalidId:
            spxLogger.logAction('GET_SNIP', request.remote_addr, 'FAIL', obj=uid)
            ret = {'rc': -1, 'error': 'The ID you provided is malformed'}
        except Exception as e:
            spxLogger.logAction('GET_SNIP', request.remote_addr, 'FAIL', obj=e)
            ret = {'rc': -1, 'error': 'Something wrong happenned'}


        return Response(json.dumps(ret, cls=spxJSONEncoder), 200, [('Content-Type', 'application/json')])


class spxCleanHandler(MethodView):
    decorators = []

    def get(self, password=None):
        ret = {}
        if password is None or password != spxSnippetHandler.app.config['SECRET_KEY']:
            spxLogger.logAction('CLEAN_SNIP', request.remote_addr, 'DENY')
            return Response(json.dumps({'rc': -1, 'error': 'You are not authorized to use this function'}), 403, [('Content-Type', 'application/json')])

        retDays = 30
        daysAgo = time.time() - (retDays * 24 * 3600)
        mc = getMongo()
        c_removed = 0
        snippets = mc.findMany(cls=spxSnippet)
        for snippet in snippets:
            if snippet.created < daysAgo:
                snippet.delete()
                c_removed += 1

        ret['rc'] = 0
        ret['count'] = c_removed
        spxLogger.logAction('CLEAN_SNIP', request.remote_addr, 'ALLOW', obj=c_removed)

        return Response(json.dumps(ret, cls=spxJSONEncoder), 200, [('Content-Type', 'application/json')])


def init_app(config=None):
    app = Flask(__name__)

    spxSnippetHandler.app = app

    if config is not None:
        app.config['SECRET_KEY'] = config.get(option='secret')
        app.config['MAIL_FROM'] = config.get(option='mailfrom')
        app.config['SMTP_SERVER'] = config.get(option='smtpserver')
        mc = spxMongo()
        mc.setDBHost(config.get(option='mongohost'))
        mc.setDBPort(config.get(option='mongoport'))
        mc.setDBUsername(config.get(option='mongousername'))
        mc.setDBPassword(config.get(option='mongopassword'))
        mc.setDBName(config.get(option='mongodatabase'))

    clean_view = spxCleanHandler.as_view('clean')
    snippet_view = spxSnippetHandler.as_view('snippets')

    app.add_url_rule('/api/clean/<password>',
            methods=['GET'],
            view_func=clean_view)

    app.add_url_rule('/api/snippet',
            methods=['POST'],
            view_func=snippet_view)

    app.add_url_rule('/api/snippet/<uid>/<key>',
            methods=['GET'],
            view_func=snippet_view)

    return app

