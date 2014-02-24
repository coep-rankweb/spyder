import redis
from pyhashxx import hashxx

r = redis.Redis()

with open("data/url.txt") as f:
	for index, url in enumerate(f):
		inc_index = index + 1
		url = url.strip()
		hashed_url = hashxx(url)
		old_id =  r.get("URL2ID:" + hashed_url)
		r.set("MAP:%s" % old_id, inc_index)
		r.set("URL2ID:%s" % hashed_url, inc_index)
		r.set("ID2URL:%d" % inc_index, url)
		r.sadd("MAPPED", inc_index)
		r.sadd("MAPPED_OLD", old_id)

assert r.scard("MAPPED") == r.scard("MAPPED_OLD")

print "Mapped..."
oldf = open ("data/matrix.mtx")
newf = open ("data/web.mtx", "w")
newf.write("%%MatrixMarket matrix coordinate real general\n%\n\n")

num_edges = 0
for i, line in enumerate(oldf):
	if i % 10000 == 0:
		print "Matrix file:", i
	row, col, val = line.strip().split()
	u = r.get("MAP:" + row)
	if u:
		v = r.get("MAP:" + col)
		if v:
			newf.write("%s\t%s\t%s\n" % (u, v, val))
			num_edges += 1
			r.sadd("IN_LINKS:%s" % v, u)
			r.sadd("OUT_LINKS:%s" % u, v)

print "done creating web.mtx"
for i in r.smembers ("URL_SET"):
	if not r.sismember("MAPPED", i):
		url = r.get("ID2URL:%s" % i)
		r.delete("ID2URL:%s" % i)

print "destroyed all evidence of incorrect mappings."

oldf.close()
newf.close()

for word in r.smembers("WORD_SET"):
	word_id = r.get("WORD2ID:" + word)
	for u in r.smembers("WORD_IN:" + word_id):
		uid = r.get("MAP:" + u)
		if uid:
			r.sadd("FOUND_IN:" + word_id, uid)
	r.delete("WORD_IN:" + word_id)

for i in r.smembers("MAPPED_OLD"):
	r.delete("MAP:" + i)

print "Num nodes:", r.scard("MAPPED")
print "Num edges:", num_edges



r.delete("URL_SET")
r.delete("MAPPED_OLD")
r.delete("MAPPED")
