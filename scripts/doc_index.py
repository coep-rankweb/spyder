'''
This program builds the document vectors and stores them in redis.
'''

import redis
import os
import shelve
from itertools import izip
from pyhashxx import hashxx

base = "/home/nvidia/kernel_panic/core/spyder/"
url_file = os.path.join(base, "data/url.txt")
keyword_file = os.path.join(base, "data/keywords.txt")

# Namespaces
DOC_VECTOR = "URL_VECTOR"
WORD2ID = "WORD2ID"

r = redis.Redis()
s = shelve.open(os.path.join(base, "data/word.shelf"))

i = 0
with open(url_file) as furl, open(keyword_file) as fkey:
	for url, keywords in izip(furl, fkey):
		klist = keywords.strip().split(',')[:-1]
		kid_list = [s[x] for x in klist]
		#kid_list = [r.get("WORD2ID:%s" % x) for x in klist]
		url_hash = hashxx(url.strip())

		if i % 10000 == 0: print i
		i += 1

		r.sadd("%s:%s" % (DOC_VECTOR, url_hash), *kid_list)
