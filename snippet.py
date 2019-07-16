import os

from spx.spxconfig import spxConfig
from spx.spxlogger import spxLogger
from spx.spxflask import init_app

"""
" This is looking at the config.ini and setting up the necessary
" logging objects in spxLogger.
"""
def initLogConfig(config):
    try:
        file_log = config.get(option='file_log')
    except:
        file_log = None
    spxLogger.logFile = file_log
    spxLogger.logSyslog = None
    spxLogger.logMongo = None
    spxLogger.setup()

config = spxConfig(os.path.dirname(os.path.realpath(__file__))+'/config.ini')
config.read()
initLogConfig(config)

app = init_app(config)

debug_mode = False
if config.get(option='debug_mode') == 'True':
    debug_mode = True

app.debug = debug_mode

if __name__ == "__main__":

    hostname = config.get(option='listen_host')
    port = int(config.get(option='listen_port'))

    app.run(host=hostname, port=port)

