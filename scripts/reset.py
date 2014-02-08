'''
removes all url - id, word - url mappings from redis
'''


import sys
sys.path.append("../")
from datastore import Datastore
r = Datastore()

r.flushdb()
