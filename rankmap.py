import redis
import sys

r = redis.Redis()

DEFAULT = "../cusp/b_cpu"
RANK = "RANK"
SORTED_WORD_IN = "SORTED_WORD_IN"

try:
	f = open (sys.argv[1])
except IndexError:
	f = open (DEFAULT)

for i, l in enumerate(f):
	r.set(RANK + ":" + str(i + 1), l)

f.close ()

for word in r.smembers("WORD_SET"):
	for u in r.smembers
