
import logging
from logging.handlers import SysLogHandler
from logging import FileHandler

class spxLogger(object):
    logFile = None
    logMongo = False
    logSyslog = None
    _logger = None

    @staticmethod
    def setup():
        if spxLogger._logger is None:
            spxLogger._logger = logging.getLogger('zfsKeyAudit')
            formatter = logging.Formatter('%(asctime)s AUDIT %(message)s')
            spxLogger._logger.setLevel(logging.WARNING)

        if spxLogger.logFile:
            file_hdlr = FileHandler(spxLogger.logFile)
            file_hdlr.setFormatter(formatter)
            spxLogger._logger.addHandler(file_hdlr)

        if spxLogger.logSyslog:
            # FIXME: make address being something configurable
            syslog_hdlr = SysLogHandler(address='/dev/log', facility=spxLogger.logSyslog)
            syslog_hdlr.setFormatter(formatter)

    @staticmethod
    def logError(msg):
        if spxLogger._logger:
            spxLogger._logger.error(msg)

    @staticmethod
    def logAction(what, src, dec, who=None, obj=None):
        if spxLogger._logger:
            msg = '[' + dec + '] ' + src + '/' + str(who) + ': ' + what + '/' + str(obj)
            spxLogger._logger.warning(msg)

    @staticmethod
    def logWarning(msg):
        if spxLogger._logger:
            spxLogger._logger.warning(msg)

