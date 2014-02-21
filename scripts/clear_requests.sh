#!/bin/bash
# Does not simply clear requests

#truncate -s 0 /home/nvidia/kernel_panic/core/spyder/data/google_spider/requests.seen
#truncate -s 0 /home/nvidia/kernel_panic/core/spyder/data/google_spider/requests.queue/*
wc -l /home/nvidia/kernel_panic/core/spyder/data/* | python /home/nvidia/kernel_panic/core/spyder/scripts/line_counter.py
