'''
removes all url - id, word - url mappings from redis
'''


import redis
r = redis.Redis()

URL_TO_ID = "URL2ID"
URL_SET = "URL_SET"
ID_TO_URL = "ID2URL"
WORD_SET = "WORD_SET"
WORD_IN = "WORD_IN"


for i in r.smembers(URL_SET):
	ID = r.get("%s:%s" % (URL_TO_ID, i))
	r.delete("%s:%s" % (ID_TO_URL, ID))
	r.delete("%s:%s" % (URL_TO_ID, i))

for w in r.smembers(WORD_SET):
	r.delete("%s:%s" % (WORD_IN, w))

r.delete(URL_SET)
r.delete(WORD_SET)
