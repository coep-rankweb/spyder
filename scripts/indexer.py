import os
import redis
from pyhashxx import hashxx

r = redis.Redis()

base = "/home/nvidia/kernel_panic/core/spyder/"
url_file = os.path.join(base, "data/url.txt")
old_matrix_file = os.path.join(base, "data/out_matrix.mtx")
new_matrix_file = os.path.join(base, "data/web.mtx")

index = 1
with open(url_file) as f:
	for url in f:
		url_hash = hashxx(url.strip())
		r.set("HASH2ID:%s" % url_hash, index)
		index += 1

		if index % 10000 == 0: print index

print "HASH2ID created"

with open(old_matrix_file) as f, open(new_matrix_file, "w") as g:
	g.write("%%MatrixMarket matrix coordinate real general\n%\n\n")
	for line, row in enumerate(f):
		u, v, val = row.strip().split()
		i = r.get("HASH2ID:%s" % u)	#must have been processed
		if not i: continue
		if r.sismember("PROCESSED_SET", v):
			j = r.get("HASH2ID:%s" % v)	#must have been processed
			g.write("%s\t%s\t%s\n" % (i, j, val))

		if line % 100000 == 0: print line
print "Web Created"

r.delete("URL_SET")
r.delete("PROCESSED_SET")
