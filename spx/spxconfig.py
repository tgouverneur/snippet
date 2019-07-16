import configparser

class spxConfig(object):
    def __init__(self, filename='./config.ini'):
        self.filename = filename
        self.config = configparser.ConfigParser()

    def configSectionMap(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
            except:
                print("ConfigException on %s!" % option)
                dict1[option] = None
        return dict1

    def read(self):
        self.config.read(self.filename)

    def get(self, section='general', option='name'):
        return self.configSectionMap(section)[option]
