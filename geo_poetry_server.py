from flask import Flask, jsonify, request, abort
from ConfigParser import SafeConfigParser
from geo_twitter import GeoTweets
from markov_text import MarkovGenerator
import os
from datetime import datetime

HEADER_KEY_ACCESS_TOKEN_KEY = "X-TwitterAuthAccessTokenKey"
HEADER_KEY_ACCESS_TOKEN_SECRET = "X-TwitterAuthAccessTokenSecret"
CONF_FILE_PATH = "/scratch/twitter.conf"
MARKOV_DEPTH = 2
MARKOV_DB_FOLDER = "/scratch/markov_dbs/"
POEM_LINES_TO_GENERATE = 3

app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({'up': True, 'version': "0.0"})

@app.route("/geo-poetry")
def get_geo_poetry():
	# Handle headers (Twitter auth credentials)
	try:
		access_token_key = request.headers[HEADER_KEY_ACCESS_TOKEN_KEY]
		access_token_secret = request.headers[HEADER_KEY_ACCESS_TOKEN_SECRET]
	except KeyError:
		abort(403)
	
	# TODO Error handling
	
	# Fetch Tweets
	tweets = GeoTweets(consumer_key, consumer_secret, access_token_key, access_token_secret)

	# Generate poetry
	random_stamp = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
	filename = datetime.utcnow().isoformat() + '_' + random_stamp
	markov_db_file = os.path.join(MARKOV_DB_FOLDER, filename)
	poems = MarkovGenerator(tweets.Tweets(), MARKOV_DEPTH, markov_db_file)
	poetry = '\n'.join(poems.next() for _ in range(POEM_LINES_TO_GENERATE))

	# TODO Get music recommendations

	# TODO JSON Response


if __name__ == "__main__":
	# Read config file
	conf = SafeConfigParser()
	conf.read(CONF_FILE_PATH)
	consumer_key = conf.get('Twitter', 'consumer_key')
	consumer_secret = conf.get('Twitter', 'consumer_secret')

	app.debug = True #TODO Do NOT use debug mode in production
	app.run()