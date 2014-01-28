'''
removes all url - id, word - url mappings from redis
'''


import sys
sys.path.append("../")
from datastore import Datastore
r = Datastore()

URL_TO_ID = "URL2ID"
URL_SET = "URL_SET"
ID_TO_URL = "ID2URL"
WORD_SET = "WORD_SET"
WORD_IN = "WORD_IN"
DIGRAM_SET = "DIGRAM_SET"
DIGRAM = "DIGRAM"
OCCUR_SET = "OCCUR_SET"
OCCUR = "OCCUR"


DOMAIN_SET = "DOMAIN_SET"
DOMAIN = "DOMAIN"

for i in r.smembers(URL_SET):
	ID = r.get("%s:%s" % (URL_TO_ID, i))
	r.delete("%s:%s" % (ID_TO_URL, ID))
	r.delete("%s:%s" % (URL_TO_ID, i))

for w in r.smembers(WORD_SET):
	r.delete("%s:%s" % (WORD_IN, w))

for d in r.smembers(DOMAIN_SET):
	r.delete("%s:%s" % (DOMAIN, d))

for digram in r.smembers(DIGRAM_SET):
	r.delete("%s:%s" % (DIGRAM, digram))

for occur in r.smembers(OCCUR_SET):
	r.delete("%s:%s" % (OCCUR, occur))

r.delete(DOMAIN_SET)
r.delete(URL_SET)
r.delete(WORD_SET)
r.delete(DIGRAM_SET)
r.delete(OCCUR_SET)
