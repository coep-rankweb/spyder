import redis

r = redis.Redis()

def reset(): r.flushdb()

def on(): r.set("POWER_SWITCH", "ON")

def off(): r.set("POWER_SWITCH", "OFF")
