import redis
from itertools import izip
import sys

r = redis.Redis()

DEFAULT = "/home/nvdia/kernel_panic/core/cusp/b_cpu"
URL_FILE = "/home/nvdia/kernel_panic/core/spyder/data/url.txt"
RANK = "RANK"
SORTED_WORD_IN = "SORTED_WORD_IN"
WORD2ID = "WORD2ID"
WORD_IN = "WORD_IN"

RANK_FILE = sys.argv[1] if len(sys.argv) == 1 else DEFAULT
with open(RANK_FILE) as f, open(URL_FILE) as g:
	for rank, url in izip(f, g):
		r.set("%s:%s" % (RANK, hashxx(url.strip())), rank.strip())

for word in r.smembers("WORD_SET"):
	word_id = r.get("%s:%s" % (WORD2ID, word))
	for url_hash in r.smembers("%s:%s" % (WORD_IN, word_id)):
		rank = r.get("%s:%s" % (RANK, url_hash))
		r.zadd("%s:%s" % (SORTED_WORD_IN, word_id), url_hash, float(rank))

# to be commented if everything screws up
for word in r.smembers("WORD_SET"):
	word_id = r.get("%s:%s" % (WORD2ID, word))
	r.delete("%s:%s" % (WORD_IN, word_id))
