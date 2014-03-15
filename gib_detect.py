#!/usr/bin/python

import pickle
import sys
import gib_detect_train

model_data = pickle.load(open('gib_model.pki', 'rb'))

def gib_detect(l):
	model_mat = model_data['mat']
	threshold = model_data['thresh']
	return gib_detect_train.avg_transition_prob(l, model_mat) > threshold

if __name__ == "__main__":
	while True:
		try:
			l = raw_input()
			print gib_detect(l)
		except EOFError:
			sys.exit(0)
