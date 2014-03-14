import redis
from itertools import izip
import sys
from pyhashxx import hashxx

remote_r = redis.Redis("10.1.99.15")
local_r = redis.Redis()

DEFAULT = "/home/nvidia/kernel_panic/core/cusp/a_gpu"
#URL_FILE = "/home/nvidia/Documents/save_28_02/url.txt"
URL_FILE = "/home/nvidia/kernel_panic/core/spyder/data/url.txt"
RANK = "RANK"
SORTED_WORD_IN = "SORTED_WORD_IN"
WORD2ID = "WORD2ID"
WORD_IN = "WORD_IN"

RANK_FILE = sys.argv[1] if len(sys.argv) == 2 else DEFAULT
with open(RANK_FILE) as f, open(URL_FILE) as g:
	for rank, url in izip(f, g):
		remote_r.set("%s:%s" % (RANK, hashxx(url.strip())), rank.strip())

print "Built RANK index"

i = 0
for word in remote_r.smembers("WORD_SET"):
	word_id = remote_r.get("%s:%s" % (WORD2ID, word))

	l = local_r.smembers("%s:%s" % (WORD_IN, word_id))
	local_r.delete("%s:%s" % (WORD_IN, word_id))
	for url_hash in l:
		rank = remote_r.get("%s:%s" % (RANK, url_hash))
		local_r.zadd("%s:%s" % (SORTED_WORD_IN, word_id), url_hash, float(rank))

	if i % 10000 == 0: print i
	i += 1

remote_r.delete("WORD_SET")
