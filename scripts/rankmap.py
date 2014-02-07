import redis
import sys

r = redis.Redis()

DEFAULT = "../cusp/b_cpu"
RANK = "RANK"
SORTED_WORD_IN = "SORTED_WORD_IN"
WORD2ID = "WORD2ID"
FOUND_IN = "FOUND_IN"

try:
	f = open (sys.argv[1])
except IndexError:
	f = open (DEFAULT)

for i, l in enumerate(f):
	r.set(RANK + ":" + str(i + 1), l.strip())

f.close ()

for word in r.smembers("WORD_SET"):
	word_id = r.get(WORD2ID + ":" + word)
	for url_id in r.smembers(FOUND_IN + ":" + word_id):
		rank = r.get(RANK + ":" + url_id)
		r.zadd(SORTED_WORD_IN + ":" + word_id, url_id, float(rank))

# to be commented if everything screws up
for word in r.smembers("WORD_SET"):
	word_id = r.get(WORD2ID + ":" + word)
	r.delete(FOUND_IN + ":" + word_id)
