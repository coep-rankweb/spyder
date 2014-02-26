import redis
from pyhashxx import hashxx

r = redis.Redis()

index = 1
with open("data/url.txt") as f:
	for url in f:
		url_hash = hashxx(url.strip())
		#r.set("ID2URL:%s" % index, url)
		#r.set("URL2ID:%s" % url_hash, index)
		r.set("HASH2ID:%s" % url_hash, index)
		index += 1

with open("data/matrix.mtx") as f, open("data/web.mtx", "w") as g:
	g.write("%%MatrixMarket matrix coordinate real general\n%\n\n")
	for row in f:
		u, v, val = row.strip().split()
		i = r.get("HASH2ID:%s" % u)	#must have been processed
		if r.sismember("PROCESSED_SET", v):
			j = r.get("HASH2ID:%s" % v)	#must have been processed
			g.write("%s\t%s\t%s\n" % (i, j, val))
