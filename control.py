import redis

remote_r = redis.Redis("10.1.99.15")
local_r = redis.Redis()

def reset():
	remote_r.flushdb()
	local_r.flushdb()

def on(): remote_r.set("POWER_SWITCH", "ON")

def off(): remote_r.set("POWER_SWITCH", "OFF")
