'''
This program builds the document vectors and stores them in redis.
'''

import sys
sys.path.append("../")
from datastore import Datastore
import os
from itertools import izip

base = "/home/nvdia/kernel_panic/core/spyder/"
url_file = "data/url.txt"
keyword_file = "data/keywords.txt"

# Namespaces
DOC_VECTOR = "DOC_VECTOR"
URL2ID = "URL2ID"
WORD2ID = "WORD2ID"


r = Datastore.factory()

furl = open (os.path.join(base, url_file))
fkeyword = open (os.path.join(base, keyword_file))

for url, keywords in izip(furl, fkeyword):

	url_id = r.get(URL2ID + ":" + url.strip())
	keyword_list = keywords.strip().split(',')[:-1]

	for keyword in keyword_list:
		keyword_id = r.get(WORD2ID + ":" + keyword)
		r.sadd(DOC_VECTOR + ":" + url_id, keyword_id)


furl.close()
fkeyword.close()
