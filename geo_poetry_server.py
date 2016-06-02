"""
The main server program. Spins up a Flask instance with the necessary methods.

Expects Twitter API keys to be stored in scratch/twitter.conf in the current working directory.
"""
from flask import Flask, jsonify, request, abort
from ConfigParser import SafeConfigParser
from common_types import Location
import geo_twitter
import markov_text
import os
import tempfile

# The actual consumer key & secret are read from a config file during startup,
# but we need unique values here for testing purposes. See test/test_geo_poetry_server.py
TWITTER_CONSUMER_KEY = "TwitterConsumerKey"
TWITTER_CONSUMER_SECRET = "TwitterConsumerSecret"
CONF_FILE_PATH = "/scratch/twitter.conf" # TODO Change location in production.
MARKOV_DEPTH = 2
POEM_LINES_TO_GENERATE = 3
RESPONSE_KEY_POETRY = 'poetry'
DEFAULT_RADIUS = 10
DEFAULT_IMPERIAL_UNITS = False

app = Flask(__name__)

@app.route("/ping")
def ping():
	"""
	Simple server ping method.

	Route: /ping
	HTTP Methods supported: GET
	@return: A JSON object with two attributes: 'up' (true), 'version' (a version string).
	"""
    return jsonify({'up': True, 'version': "0.0"})

@app.route("/geo-poetry", methods=['POST'])
def get_geo_poetry():
	"""
	The main server method to fetch "poetry" and mood music.

	Route: /geo-poetry
	HTTP Methods supported: POST
	@type location: application/json (POST data)
	@param location: A JSON object with 4 attributes: 'latitude' (float), 'longitude' (float), 'radius' (int), imperial_units (bool)
	@rtype: application/json
	@return: A JSON object with 2 attributes: 'poetry' (the generated poetry as string), 'track' (spotify URI)
	"""
	try:
		json_data = request.get_json()
		latitude = float(json_data['latitude'])
		longitude = float(json_data['longitude'])
		try:
			radius = int(json_data['radius'])
			imperial_units = json_data['imperial_units']
			assert isinstance(imperial_units, bool)
		except KeyError: # radius and imperial_units are optional arguments
			radius = DEFAULT_RADIUS
			imperial_units = DEFAULT_IMPERIAL_UNITS
		location = Location(latitude, longitude, radius, imperial_units)
	except KeyError as err:
		app.logger.warning('geo-poetry request missing '+err.message) #err.message will be 'longitude' or 'latitude'
		abort(400)
	except ValueError as err:
		app.logger.warning('geo-poetry given a non-numerical argument: '+err.message)
		abort(400)
	except AssertionError as err:
		app.logger.warning('geo-poetry given a non-boolean for imperial_units')
		abort(400)

	# Fetch Tweets
	tweets = geo_twitter.GeoTweets(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)

	# Generate poetry
	#TODO use tempfile module instead
	markov_db_file, markov_db_filepath = tempfile.mkstemp(suffix='db')
	poems = markov_text.MarkovGenerator(tweets.Tweets(location), MARKOV_DEPTH, markov_db_file)
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