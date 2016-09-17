"""
The main server program. Spins up a Flask instance with the necessary methods.

Expects Twitter API keys to be stored in scratch/twitter.conf in the current working directory.
"""
from flask import Flask, jsonify, request, abort
from flask.ext.cors import CORS
from ConfigParser import SafeConfigParser
from common_types import Location
import geo_twitter
import markov_text
import vaderSentiment.vaderSentiment
import spotipy
import spotipy.oauth2

VERSION = "0.2"

# The actual credentials are read from a config file during startup,
# but we need unique values here for testing purposes. See test/test_geo_poetry_server.py
TWITTER_CONSUMER_KEY = "TwitterConsumerKey"
TWITTER_CONSUMER_SECRET = "TwitterConsumerSecret"
SPOTIFY_CLIENT_ID = "SpotifyClientID"
SPOTIFY_CLIENT_SECRET = "SpotifyClientSecret"
CONF_FILE_PATH = "conf/server.conf"

RESPONSE_KEY_POETRY = 'poetry'
RESPONSE_KEY_TWEETS_READ_COUNT = 'num_source_tweets'
RESPONSE_KEY_AVG_SENTIMENT = 'sentiment'
RESPONSE_KEY_TRACK = 'track'
RESPONSE_KEY_GENRE = 'genre'

MAX_TWEETS_TO_READ = 500
MIN_TWEETS_TO_READ = 100
MARKOV_DEPTH = 2
POEM_LINES_TO_GENERATE = 3

DEFAULT_RADIUS = 10
DEFAULT_IMPERIAL_UNITS = False
SENTIMENT_MIN_MAGNITUDE = 0.2
SPOTIFY_DEFAULT_GENRE = 'ambient'
SPOTIFY_DEFAULT_ENERGY = 0.5

LOG_TWEETS = False


app = Flask(__name__)
CORS(app)

@app.route("/ping")
def ping():
	"""
	Simple server ping method.
	
	Route: /ping
	HTTP Methods supported: GET
	@return: A JSON object with two attributes: 'up' (true), 'version' (a version string).
	"""
	return jsonify({'up': True, 'version': VERSION})

@app.route("/get-genres")
def get_genres():
	"""
	Server method that returns the list of genres available for Spotify's recommendations engine.

	Route: /get-genres
	HTTP Methods supported: GET
	@return: A JSON object with the attribute 'generes', a list of strings.
	"""
	SpotifyClientCredentials = spotipy.oauth2.SpotifyClientCredentials
	client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
	spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
	spotify_response = spotify.recommendation_genre_seeds()
	return jsonify(spotify_response)

class NoSSLException(Exception):
	"""
	Indicates that the client did not use SSL, but should have.
	"""
	pass

@app.errorhandler(NoSSLException)
def require_ssl(error):
	"""
	Error handler for when a method is called without SSL, but requires SSL.
	"""
	return 'For security of GPS coordinates, do NOT call /geo-poetry without using SSL.', 403

@app.route("/geo-poetry", methods=['POST'])
def get_geo_poetry():
	"""
	The main server method to fetch "poetry" and mood music.

	Route: /geo-poetry
	HTTP Methods supported: POST
	For security of GPS coordinates, clients must use HTTPS. If they do not,
	  this method will return 403 Forbidden
	@type arguments: application/json (POST data)
	@param arguments: A JSON object with 5 attributes:
		'latitude' (float) - required,
		'longitude' (float) - required,
		'radius' (int) - optional, default 10,
		'imperial_units' (bool) - optional, default False
		'genre' (string) - optional, default "ambient"
		'energy' (string) - optional, default 0.5
	@rtype: application/json
	@return: A JSON object with 2 attributes: 'poetry' (the generated poetry as string), 'track' (spotify URI)
	"""
	# Error if the client did not use SSL. (For local testing, ignore if debug mode.)
	if request.url.startswith('http://') and not app.debug:
		raise(NoSSLException)

	getSentiment = vaderSentiment.vaderSentiment.sentiment
	SpotifyClientCredentials = spotipy.oauth2.SpotifyClientCredentials
	
	try:
		json_data = request.get_json()
		if json_data == None:
			app.logger.warning('geo-poetry request did not contain valid JSON')
			abort(400)
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
		try:
			genre = json_data['genre']
		except KeyError:
			genre = SPOTIFY_DEFAULT_GENRE
		try:
			target_energy = float(json_data['song_energy'])
			if target_energy < 0.0 or target_energy > 1.0:
				abort(400)
		except KeyError:
			target_energy = SPOTIFY_DEFAULT_ENERGY
		except ValueError: # floating point conversion failed
			abort(400)
	except KeyError as err:
		app.logger.warning('geo-poetry request missing '+err.message) #err.message will be 'longitude' or 'latitude'
		abort(400)
	except ValueError as err:
		app.logger.warning('geo-poetry given a non-numerical argument: '+err.message)
		abort(400)
	except AssertionError as err:
		app.logger.warning('geo-poetry given a non-boolean for imperial_units')
		abort(400)

	# ===== Fetch Tweets =====
	tweets = geo_twitter.GeoTweets(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	# because both the Markov generator and sentiment analyzer need the tweets,
	#  we have to store them instead of using an iterator
	def tweet_limitor(generator):
		for i in range(MAX_TWEETS_TO_READ):
			yield generator.next()
	tweets_list = [tweet for tweet in tweet_limitor(tweets.Tweets(location, LOG_TWEETS))]
	if len(tweets_list) < MIN_TWEETS_TO_READ:
		# If we hit Twitter's rate limit, tweets.Tweets(location) will raise StopIteration early
		abort(429)

	# ===== Generate Poetry =====
	poems = markov_text.MarkovGenerator(tweets_list, MARKOV_DEPTH, ":memory:")
	poetry = "\n".join([poems.next() for _ in range(POEM_LINES_TO_GENERATE)])

	# ===== Sentiment Analysis =====
	total_sentiment = 0
	sentiment_included_count = 0
	for tweet in tweets_list:
		vs = getSentiment(tweet)
		# In order to give more variability to the results, we ignore relatively neutral tweets
		if (vs['compound'] > SENTIMENT_MIN_MAGNITUDE) or (vs['compound'] < -SENTIMENT_MIN_MAGNITUDE):
			total_sentiment += vs['compound']
			sentiment_included_count += 1
	try:
		avg_sentiment = total_sentiment / float(sentiment_included_count)
	except ZeroDivisionError:
		avg_sentiment = 0.0

	# ===== Music Recommendations =====
	client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
	spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
	normalized_sentiment = (avg_sentiment + 1.0) / 2.0 # from range [-1, 1] to range [0, 1]
	spotify_response = spotify.recommendations(
		seed_genres = [genre],
		limit=1, target_instrumentalness=1.0,
		target_energy = target_energy,
		target_valence = normalized_sentiment)
	try:
		spotify_track_uri = spotify_response['tracks'][0]['uri']
	except IndexError:
		# If the given genre doesn't exist, Spotify returns an empty list of tracks.
		app.logger.warning('No tracks returned from Spotify. Probably unknown genre: "' + genre + '"')
		abort(400)

	# ===== Build JSON Response =====
	response = {}
	response[RESPONSE_KEY_POETRY] = poetry
	response[RESPONSE_KEY_TWEETS_READ_COUNT] = len(tweets_list)
	response[RESPONSE_KEY_AVG_SENTIMENT] = avg_sentiment
	response[RESPONSE_KEY_TRACK] = spotify_track_uri
	response[RESPONSE_KEY_GENRE] = genre
	return jsonify(response)


if __name__ == "__main__":
	# Read config file
	conf = SafeConfigParser()
	conf.read(CONF_FILE_PATH)
	TWITTER_CONSUMER_KEY = conf.get('Twitter', 'consumer_key')
	TWITTER_CONSUMER_SECRET = conf.get('Twitter', 'consumer_secret')
	SPOTIFY_CLIENT_ID = conf.get('Spotify', 'client_id')
	SPOTIFY_CLIENT_SECRET = conf.get('Spotify', 'client_secret')

	app.debug = True # Do NOT use debug mode in production, it is not secure.
	app.run()