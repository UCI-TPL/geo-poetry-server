from flask import Flask, jsonify, request, abort
from ConfigParser import SafeConfigParser
import geo_twitter
import markov_text
import os
import tempfile

# The actual consumer key & secret are read from a config file during startup,
# but we need unique values here for testing purposes. See test/test_geo_poetry_server.py
TWITTER_CONSUMER_KEY = "TwitterConsumerKey"
TWITTER_CONSUMER_SECRET = "TwitterConsumerSecret"
CONF_FILE_PATH = "/scratch/twitter.conf"
MARKOV_DEPTH = 2
POEM_LINES_TO_GENERATE = 3
RESPONSE_KEY_POETRY = 'poetry'

app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({'up': True, 'version': "0.0"})

@app.route("/geo-poetry")
def get_geo_poetry():
	# Fetch Tweets
	tweets = geo_twitter.GeoTweets(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)

	# Generate poetry
	#TODO use tempfile module instead
	markov_db_file, markov_db_filepath = tempfile.mkstemp(suffix='db')
	poems = markov_text.MarkovGenerator(tweets.Tweets(), MARKOV_DEPTH, markov_db_file)
	poetry = '\n'.join([poems.next() for _ in range(POEM_LINES_TO_GENERATE)])
	os.close(markov_db_file)
	os.unlink(markov_db_filepath)

	# TODO Get music recommendations

	# Build JSON Response
	response = {}
	response[RESPONSE_KEY_POETRY] = poetry
	return jsonify(response)


if __name__ == "__main__":
	# Read config file
	conf = SafeConfigParser()
	conf.read(CONF_FILE_PATH)
	TWITTER_CONSUMER_KEY = conf.get('Twitter', 'consumer_key')
	TWITTER_CONSUMER_SECRET = conf.get('Twitter', 'consumer_secret')

	app.debug = True #TODO Do NOT use debug mode in production
	app.run()