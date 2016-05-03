# -*- coding: UTF-8 -*-
import re
import sys
import random
import string
import twitter
from markov_text import MarkovGenerator
from ConfigParser import SafeConfigParser

URL_REGEX = r'(https?://\S*)' # Eh, good enough for my purposes

def get_user_statuses(username):
	# TODO Fetch more than 200 tweets using cursors
	statuses = api.GetUserTimeline(screen_name=username, count=200)
	for s in statuses:
		yield s.text

def clean_user_statuses(status_list):
	for s in status_list:
		s_clean = re.sub(URL_REGEX, '', s) # Remove URLs
		s_clean = re.sub(r'@\w+', '', s_clean) # Remove mentions
		s_clean = re.sub(r'#\w+', '', s_clean) # Remove hashtags
		yield s_clean

def get_random_string(size):
	return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(size)])

if __name__ == '__main__':
	args = sys.argv
	usage = 'Usage: %s <config_file> <username> <markov_depth> <number_to_generate>' % (args[0], )

	if len(args) < 5:
		raise ValueError(usage)
	config_file = args[1]
	username = args[2]
	markov_depth = int(args[3])
	number_to_generate = int(args[4])

	conf = SafeConfigParser()
	conf.read(config_file)
	consumer_key = conf.get('Twitter', 'consumer_key')
	consumer_secret = conf.get('Twitter', 'consumer_secret')
	access_token_key = conf.get('Twitter', 'access_token_key')
	access_token_secret = conf.get('Twitter', 'access_token_secret')

	api = twitter.Api(consumer_key=consumer_key,
					consumer_secret=consumer_secret,
					access_token_key=access_token_key,
					access_token_secret=access_token_secret)
	#print(api.VerifyCredentials()) # DEBUG

	statuses = get_user_statuses(username)
	statuses_clean = clean_user_statuses(statuses)
	# sqlite will update the database file, not overwrite, so we use a new random file each time
	generator = MarkovGenerator(statuses_clean, markov_depth, 'scratch/_'+get_random_string(32)+'.db')
	for i in range(number_to_generate):
		print generator.next()
