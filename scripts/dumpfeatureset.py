import redis
import shelve

r = redis.Redis()
s = shelve.open("feature_dump")

for i in r.keys("FEA*"):
	s[i] = r.get(i)
s.close()
