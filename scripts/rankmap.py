import redis
from itertools import izip
import sys
from pyhashxx import hashxx

r = redis.Redis()

DEFAULT = "/home/nvidia/kernel_panic/core/cusp/a_gpu"
URL_FILE = "/home/nvidia/Documents/save_28_02/url.txt"
RANK = "RANK"
SORTED_WORD_IN = "SORTED_WORD_IN"
WORD2ID = "WORD2ID"
WORD_IN = "WORD_IN"

RANK_FILE = sys.argv[1] if len(sys.argv) == 2 else DEFAULT
with open(RANK_FILE) as f, open(URL_FILE) as g:
	for rank, url in izip(f, g):
		r.set("%s:%s" % (RANK, hashxx(url.strip())), rank.strip())

print "Built RANK index"

i = 0
for word in r.smembers("WORD_SET"):
	word_id = r.get("%s:%s" % (WORD2ID, word))

	l = r.smembers("%s:%s" % (WORD_IN, word_id))
	r.delete("%s:%s" % (WORD_IN, word_id))
	for url_hash in l:
		rank = r.get("%s:%s" % (RANK, url_hash))
		r.zadd("%s:%s" % (SORTED_WORD_IN, word_id), url_hash, float(rank))

	if i % 10000 == 0: print i
	i += 1

r.delete("WORD_SET")
