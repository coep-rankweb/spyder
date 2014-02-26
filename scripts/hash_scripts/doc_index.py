'''
This program builds the document vectors and stores them in redis.
'''

import redis
import os
from itertools import izip
from pyhashxx import hashxx

base = "/home/nvdia/kernel_panic/core/spyder/"
url_file = os.path.join(base, "data/url.txt")
keyword_file = os.path.join(base, "data/keywords.txt")

# Namespaces
DOC_VECTOR = "URL_VECTOR"
URL2ID = "N:URL2ID"
WORD2ID = "WORD2ID"


r = redis.Redis()

with open(url_file) as furl, open(keyword_file) as fkey:
	for url, keywords in izip(furl, fkey):
		klist = keywords.strip().split(',')[:-1]
		kid_list = [r.get("WORD2ID:%s" % x) for x in klist]
		url_hash = hashxx(url.strip())

		r.sadd("%s:%s" % (DOC_VECTOR, url_hash), *kid_list)
