#!/bin/bash
# Does not simply clear requests

truncate -s 0 $HOME/kernel_panic/core/spyder/data/google_spider/requests.seen
truncate -s 0 $HOME/kernel_panic/core/spyder/data/google_spider/requests.queue/*
wc -l $HOME/kernel_panic/core/spyder/data/* | python $HOME/kernel_panic/core/spyder/scripts/line_counter.py
