from flask import Flask, jsonify, request, abort
from ConfigParser import SafeConfigParser
from geo_twitter import GeoTweets
from markov_text import MarkovGenerator
import os
from datetime import datetime
from twython import TwythonAuthError

# The actual consumer key & secret are read from a config file during startup,
# but we need unique values here for testing purposes. See test/test_geo_poetry_server.py
TWITTER_CONSUMER_KEY = "TwitterConsumerKey"
TWITTER_CONSUMER_SECRET = "TwitterConsumerSecret"
HEADER_KEY_ACCESS_TOKEN_KEY = "TwitterAuthAccessTokenKey"
HEADER_KEY_ACCESS_TOKEN_SECRET = "X-Twitterauthaccesstokensecret"
CONF_FILE_PATH = "/scratch/twitter.conf"
MARKOV_DEPTH = 2
MARKOV_DB_FOLDER = "/scratch/markov_dbs/"
POEM_LINES_TO_GENERATE = 3
RESPONSE_KEY_POETRY = 'poetry'

app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({'up': True, 'version': "0.0"})

@app.route("/geo-poetry")
def get_geo_poetry():
	try:
		# Handle headers (Twitter auth credentials)
		print request.headers[HEADER_KEY_ACCESS_TOKEN_KEY]
		try:
			access_token_key = request.headers[HEADER_KEY_ACCESS_TOKEN_KEY]
			access_token_secret = request.headers[HEADER_KEY_ACCESS_TOKEN_SECRET]
		except KeyError as err:
			print 'Received geo-poetry request without header '+str(err.message)
			app.logger.error('Received geo-poetry request without header '+str(err.message))
			abort(403)

		# Fetch Tweets
		try:
			tweets = GeoTweets(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, access_token_key, access_token_secret)
		except TwythonAuthError as err:
			app.logger.error('Twitter authentication failed: ' + str(err))
			abort(403)

		# Generate poetry
		#TODO use tempfile module instead
		random_stamp = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
		filename = datetime.utcnow().isoformat() + '_' + random_stamp
		markov_db_file = os.path.join(MARKOV_DB_FOLDER, filename)
		poems = MarkovGenerator(tweets.Tweets(), MARKOV_DEPTH, markov_db_file)
		poetry = '\n'.join(poems.next() for _ in range(POEM_LINES_TO_GENERATE))

		# TODO Get music recommendations

		# Build JSON Response
		response = {}
		response[RESPONSE_KEY_POETRY] = poetry
		return jsonify(response)
	except Exception as err:
		app.logger.error('Unexpected Error: ' + str(err))
		raise err
		#abort(500) # TODO Abort 500 in production, raise error for debug mode during development


if __name__ == "__main__":
	# Read config file
	conf = SafeConfigParser()
	conf.read(CONF_FILE_PATH)
	TWITTER_CONSUMER_KEY = conf.get('Twitter', 'consumer_key')
	TWITTER_CONSUMER_SECRET = conf.get('Twitter', 'consumer_secret')

	app.debug = True #TODO Do NOT use debug mode in production
	app.run()