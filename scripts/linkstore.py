import redis

r = redis.Redis("10.1.99.15")

base = "/home/nvidia/kernel_panic/core/spyder/"
f_mat = os.path.join(base, "data/web.mtx")

with open(f_mat, "r") as f:
	f.next()
	f.next()
	f.next()
	for line in f:
		u, v, w = line.strip.split()
		u_hash = r.get("ID2HASH:%s" % u)
		v_hash = r.get("ID2HASH:%s" % v)
		r.sadd("IN_LINKS:%s" % u_hash, v_hash)
		r.sadd("OUT_LINKS:%s" % v_hash, u_hash)
