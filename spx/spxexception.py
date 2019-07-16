
class spxException(Exception):

    def __init__(self, msg='', rc=0):
        self.msg = msg
        self.rc = rc

    def __str__(self):
        return '[!] Exception (errno=' + str(self.rc) + '): ' + self.msg


