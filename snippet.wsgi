import sys
import os

def execfile(filename):
    globals = dict( __file__ = filename )
    exec( open(filename).read(), globals )

activate_this = os.path.dirname(os.path.realpath(__file__)) + '/bin/activate_this.py'
execfile(activate_this)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from snippet import app as application
