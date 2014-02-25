import redis
from pyhashxx import hashxx

r = redis.Redis()

with open("data/url.txt") as f:
	for index, url in enumerate(f):
		inc_index = index + 1
		url = url.strip()
		hashed_url = hashxx(url)
		r.set("N:URL2ID:%s" % hashed_url, inc_index)
		r.set("N:ID2URL:%s" % inc_index, url)

		del_url = r.get("ID2URL:%s" % inc_index)
		del_id = r.get("URL2ID:%s" % hashed_url)
		r.delete("ID2URL:%s" % del_id)
		r.delete("ID2URL:%s" % inc_index)
		r.delete("URL2ID:%d" % hashxx(del_url))
		r.delete("URL2ID:%d" % hashed_url)

for u in r.smembers("URL_SET"):
	url = r.get("ID2URL:%s" % u)
	r.delete("ID2URL:%s" % u)
	r.delete("URL2ID:%d" % hashxx(url))


print "Mapped..."
oldf = open ("data/matrix.mtx")
newf = open ("data/web.mtx", "w")
newf.write("%%MatrixMarket matrix coordinate real general\n%\n\n")

num_edges = 0
for i, line in enumerate(oldf):
	if i % 10000 == 0:
		print "Matrix file:", i
	row, col, val = line.strip().split()
	u = r.get("N:URL2ID:" + row)
	if u:
		v = r.get("N:URL2ID:" + col)
		if v:
			newf.write("%s\t%s\t%s\n" % (u, v, val))
			num_edges += 1
			r.sadd("IN_LINKS:%s" % v, u)
			r.sadd("OUT_LINKS:%s" % u, v)

print "done creating web.mtx"

oldf.close()
newf.close()

for word in r.smembers("WORD_SET"):
	word_id = r.get("WORD2ID:" + word)

	for u in r.smembers("WORD_IN:%s" % word_id):
		uid = r.get("N:ID2URL:%s" % u)
		if not uid: r.srem("WORD_IN:%s" % word_id, u)

print "Num edges:", num_edges

r.delete("URL_SET")
