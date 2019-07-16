from io import StringIO
import json
import time
import os
import re
import base64
import requests
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from spx.xss import XssCleaner
from simplejson import JSONEncoder
from bson.objectid import ObjectId

from Crypto import Random
from Crypto.Cipher import AES

from spx.spxutils import randString
from spx.spxlogger import spxLogger
from spx.spxmongo import spxMongoObject, spxMongo
from spx.spxexception import spxException

class spxSnippet(spxMongoObject):

    signature = '---snippet---'

    _collection = 'snippets'
    _attr_ids = ['id']
    _attrs = {
            'id': '_id',
            'content': 'content',
            'reference': 'reference',
            'email': 'email',
            'createdBy': 'createdBy',
            'isRaw': 'isRaw',
            'isConfirm': 'isConfirm',
            'created': 'created',
            }

    def __init__(self, id=None, content='', createdBy=None, created=None):

        self.id = id
        if self.id is None:
            self.id = ObjectId()
        self.content = content
        self.createdBy = createdBy
        self.isRaw = False
        self.isConfirm = False
        self.email = ''
        self.reference = ''
        self.created = created
        if self.created is None:
            self.created = int(time.time())

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def __ne__(self, other):
        if self.id != other.id:
            return True
        return False

    def __str__(self):
        return str(self.id)

    def __validateEmail(self):
        if re.fullmatch(r'[^@]+@[^@]+\.[^@]+', self.email):
            return True
        return False

    def logDenied(self, host):
        spxLogger.logError('DENIED Access to ' + str(self) + ' from ' + host)

    def logAccess(self, host):
        spxLogger.logError('ALLOWED Access to ' + str(self) + ' from ' + host)

    def sendConfirmation(self, smtp_addr, mail_from, remote_addr='Unknown'):
        if len(smtp_addr) == 0:
            raise spxException(rc=-5, msg='SMTP address is not configured')

        if len(mail_from) == 0:
            raise spxException(rc=-5, msg='source email address is not configured')

        text = 'Hello,\n\nHere is your read confirmation for the snippet with refernce: ' + self.reference + '\n'
        text += 'The IP who has retreived the snippet was: ' + remote_addr + '\n\n'
        text += 'Best,\n\n--Secure Snippet\n'
        msg = MIMEMultipart()

        msg['Subject'] = '[SNIPPET] Read confirmation: ' + self.reference
        msg['From'] = mail_from
        msg['To'] = self.email
        text = MIMEText(text)
        msg.attach(text)
        with smtplib.SMTP(smtp_addr) as smtp:
            smtp.sendmail(mail_from, self.email, msg.as_string())
            smtp.quit()

    def stripXSS(self):
        x = XssCleaner(remove_all=self.isRaw)
        self.content = x.strip(self.content)

    def encrypt(self):
        self.clearKey = randString(32)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.clearKey, AES.MODE_CFB, iv)
        cryptbytes = cipher.encrypt(spxSnippet.signature + self.content)
        self.content = base64.b64encode(iv + cryptbytes)

        if len(self.email) > 0:
            self.email = base64.b64encode(cipher.encrypt(self.email))

        if len(self.reference) > 0:
            self.reference = base64.b64encode(cipher.encrypt(self.reference))

    def decrypt(self, key):
        if len(key) != 32:
            raise spxException(rc=-1, msg='Wrong key length')

        buf = base64.b64decode(self.content)
        iv = buf[:AES.block_size]
        content = buf[AES.block_size:]
        cipher = AES.new(key, AES.MODE_CFB, iv)
        content = cipher.decrypt(content).decode()
        sig = content[:len(spxSnippet.signature)]

        if sig == spxSnippet.signature:
            self.content = content[len(spxSnippet.signature):]
            """
                if we have the right signature and email/reference exist,
                we can also decrypt those
            """
            if len(self.email) > 0:
                self.email = cipher.decrypt(base64.b64decode(self.email)).decode()

            if len(self.reference) > 0:
                self.reference = cipher.decrypt(base64.b64decode(self.reference)).decode()

            return True

        return False

    def dictToObj(self, d, isBck=False):
        if not 'content' in d or len(d['content']) == 0:
            raise spxException(rc=-1, msg='content not provided')
        if not 'createdBy' in d:
            raise spxException(rc=-1, msg='createdBy not provided')

        self.isRaw = False
        self.isConfirm = False

        if 'isConfirm' in d:
            if d['isConfirm'] is True or d['isConfirm'] == 1:
                self.isConfirm = True

        if 'isRaw' in d:
            if d['isRaw'] is True or d['isRaw'] == 'True' or d['isRaw'] == 1:
                self.isRaw = True

        if self.isConfirm is True:
            if not 'email' in d or len(d['email']) == 0:
                raise spxException(rc=-2, msg='email address not provided but confirmation is enabled')
            else:
                self.email = d['email']
                if not self.__validateEmail():
                    raise spxException(rc=-3, msg='email address provided is not valid')

            if not 'reference' in d or len(d['reference']) == 0:
                raise spxException(rc=-3, msg='reference not provided but confirmation is enblaed')
            else:
                self.reference = d['reference']

        self.content = d['content']
        self.createdBy = d['createdBy']



    def objToDict(self, isBck=False):

        rs = {}
        rs['id'] = str(self.id)
        rs['content'] = self.content
        """ rs['createdBy'] = self.createdBy we don't want to disclose who has created the snippet """
        rs['created'] = self.created
        rs['isRaw'] = self.isRaw
        if isBck == True:
            rs['isConfirm'] = self.isConfirm
            rs['email'] = self.email
            rs['reference'] = self.reference

        return rs

