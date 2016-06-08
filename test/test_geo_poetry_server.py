"""
Unit tests for module L{geo_poetry_server}
"""
import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

import pytest
import geo_poetry_server
from geo_poetry_server import *
from flask import json
import fudge
from fudge.inspector import arg
from twython import TwythonAuthError
from common_types import Location

# SETUP
app.config['TESTING'] = True
client = app.test_client()

def test_ping():
	"""
	The ping method returns the JSON {'up': true, 'version': "0.0"}.

	Functions tested:
		- L{geo_poetry_server.ping}
	"""
	response = client.get("/ping")
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json['up'] == True
	assert response_json['version'] == "0.0"

@fudge.patch('geo_twitter.GeoTweets')
def test_get_geo_poetry_auth_failure(MockGeoTweets):
	"""
	The get_geo_poetry method raises TwythonAuthError if the GeoTweets constructor does.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.raises(TwythonAuthError("Example message.")))
	with pytest.raises(TwythonAuthError):
		client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')

def test_get_geo_poetry_wrong_mime_type():
	"""
	The get_geo_poetry method returns 400 Bad Request if the POST data is not application/json.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data="BlahBlahBlah", content_type='text/plain')
	assert response.status_code == 400

def test_get_geo_poetry_malformed_json():
	"""
	The get_geo_poetry method returns 400 Bad Request if the POST data is not valid JSON.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data="BlahBlahBlah", content_type='application/json')
	assert response.status_code == 400

def test_get_geo_poetry_missing_latitude():
	"""
	The get_geo_poetry method returns 400 Bad Request if the latitude attribute is missing.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data=json.dumps({
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	assert response.status_code == 400

def test_get_geo_poetry_missing_longitude():
	"""
	The get_geo_poetry method returns 400 Bad Request if the longitude attribute is missing.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	assert response.status_code == 400

def test_get_geo_poetry_bad_latitude():
	"""
	The get_geo_poetry method returns 400 Bad Request if the latitude attribute is not a number.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 'a',
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	assert response.status_code == 400

def test_get_geo_poetry_bad_longitude():
	"""
	The get_geo_poetry method returns 400 Bad Request if the longitude attribute is not a number.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0,
			'longitude' : 'a',
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	assert response.status_code == 400

def test_get_geo_poetry_bad_radius():
	"""
	The get_geo_poetry method returns 400 Bad Request if the radius attribute is not a number.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0,
			'longitude' : 0.0,
			'radius' : 'a',
			'imperial_units' : True}),
		content_type='application/json')
	assert response.status_code == 400

def test_get_geo_poetry_bad_imperial_units():
	"""
	The get_geo_poetry method returns 400 Bad Request if the imperial_units attribute is not a boolean.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : 0}),
		content_type='application/json')
	assert response.status_code == 400

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator', 
	'vaderSentiment.vaderSentiment.sentiment', 'spotipy.oauth2.SpotifyClientCredentials',
	'spotipy.Spotify')
def test_get_geo_poetry(MockGeoTweets, MockMarkovGenerator, MockGetSentiment, MockClientCredentials, MockSpotify):
	"""
	The get_geo_poetry method works as expected when given valid input.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	# Temporarily set low enough minimum number of tweets to read
	prev_min_tweets = geo_poetry_server.MIN_TWEETS_TO_READ
	geo_poetry_server.MIN_TWEETS_TO_READ = 0
	fake_tweets_list = iter(['Tweet 1', 'Tweet 2'])
	fake_poetry_line = 'A Line Of CG Poetry.'
	fake_spotify_url = 'http://www.example.com'
	fake_genre = 'MyGenre'
	def check_location_obj(obj):
		if not isinstance(obj, Location):
			return False
		if not obj.latitude == 0.0:
			return False
		if not obj.longitude == 0.0:
			return False
		if not obj.radius == 10:
			return False
		if not obj.imperial_units == True:
			return False
		return True
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.returns_fake()
		.expects('Tweets').with_args(arg.passes_test(check_location_obj))
		.returns(fake_tweets_list))
	(MockMarkovGenerator.expects_call()
		.with_args(['Tweet 1', 'Tweet 2'], MARKOV_DEPTH, ':memory:')
		.returns_fake()
		.expects('next').times_called(POEM_LINES_TO_GENERATE).returns(fake_poetry_line))
	(MockGetSentiment.expects_call()
		.with_args('Tweet 1')
		.returns({'compound': SENTIMENT_MIN_MAGNITUDE + 0.01})
		.next_call().with_args('Tweet 2')
		.returns({'compound': -(SENTIMENT_MIN_MAGNITUDE + 0.01)}))
	(MockClientCredentials.expects_call()
		.with_args(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
		.returns('Constant'))
	(MockSpotify.expects_call()
		.with_args(client_credentials_manager='Constant')
		.returns_fake()
		.expects('recommendations').with_args(
			seed_genres = [fake_genre],
			limit=1, target_instrumentalness=1.0, min_instrumentalness=SPOTIFY_MIN_INSTRUMENTALNESS,
			target_energy=0.5, target_valence = ((0.0)+1.0)/2.0)
		.returns({
				'tracks' : [ {
					'external_urls' : {
						'spotify' : fake_spotify_url
					}
				}]
			}))

	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True,
			'genre' : fake_genre}),
		content_type='application/json')
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json[RESPONSE_KEY_POETRY] == '\n'.join([fake_poetry_line for _ in range(POEM_LINES_TO_GENERATE)])
	assert response_json[RESPONSE_KEY_TWEETS_READ_COUNT] == 2
	assert response_json[RESPONSE_KEY_AVG_SENTIMENT] == 0.0
	assert response_json[RESPONSE_KEY_TRACK] == fake_spotify_url

	# Set MIN_TWEETS_TO_READ back to normal
	geo_poetry_server.MIN_TWEETS_TO_READ = prev_min_tweets

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator')
def test_get_geo_poetry_rate_limit(MockGeoTweets, MockMarkovGenerator):
	"""
	The get_geo_poetry method returns 429 Too Many Requests if the tweet count is below MIN_TWEETS_TO_READ.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	# Temporarily set correct minimum number of tweets to read
	prev_min_tweets = geo_poetry_server.MIN_TWEETS_TO_READ
	geo_poetry_server.MIN_TWEETS_TO_READ = 3
	fake_tweets_list = iter(['Tweet 1', 'Tweet 2'])
	fake_poetry_line = 'A Line Of CG Poetry.'
	def check_location_obj(obj):
		if not isinstance(obj, Location):
			return False
		if not obj.latitude == 0.0:
			return False
		if not obj.longitude == 0.0:
			return False
		if not obj.radius == 10:
			return False
		if not obj.imperial_units == True:
			return False
		return True
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.returns_fake()
		.expects('Tweets').with_args(arg.passes_test(check_location_obj))
		.returns(fake_tweets_list))

	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	assert response.status_code == 429

	# Set MIN_TWEETS_TO_READ back to normal
	geo_poetry_server.MIN_TWEETS_TO_READ = prev_min_tweets

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator', 
	'vaderSentiment.vaderSentiment.sentiment', 'spotipy.oauth2.SpotifyClientCredentials',
	'spotipy.Spotify')
def test_get_geo_poetry_tweet_limiting(MockGeoTweets, MockMarkovGenerator, MockGetSentiment, MockClientCredentials, MockSpotify):
	"""
	The get_geo_poetry method correctly truncates the tweet list to MAX_TWEETS_TO_READ.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	# Temporarily set correct minimum & maximum number of tweets to read
	prev_min_tweets = geo_poetry_server.MIN_TWEETS_TO_READ
	prev_max_tweets = geo_poetry_server.MAX_TWEETS_TO_READ
	geo_poetry_server.MIN_TWEETS_TO_READ = 0
	geo_poetry_server.MAX_TWEETS_TO_READ = 1
	fake_tweets_list = iter(['Tweet 1', 'Tweet 2'])
	fake_poetry_line = 'A Line Of CG Poetry.'
	fake_spotify_url = 'http://www.example.com'
	def check_location_obj(obj):
		if not isinstance(obj, Location):
			return False
		if not obj.latitude == 0.0:
			return False
		if not obj.longitude == 0.0:
			return False
		if not obj.radius == 10:
			return False
		if not obj.imperial_units == True:
			return False
		return True
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.returns_fake()
		.expects('Tweets').with_args(arg.passes_test(check_location_obj))
		.returns(fake_tweets_list))
	(MockMarkovGenerator.expects_call()
		.with_args(['Tweet 1'], MARKOV_DEPTH, ':memory:')
		.returns_fake()
		.expects('next').times_called(POEM_LINES_TO_GENERATE).returns(fake_poetry_line))
	(MockGetSentiment.expects_call()
		.with_args('Tweet 1')
		.returns({'compound': SENTIMENT_MIN_MAGNITUDE + 0.01}))
	(MockClientCredentials.expects_call()
		.with_args(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
		.returns('Constant'))
	(MockSpotify.expects_call()
		.with_args(client_credentials_manager='Constant')
		.returns_fake()
		.expects('recommendations').with_args(
			seed_genres = [SPOTIFY_DEFAULT_GENRE],
			limit=1, target_instrumentalness=1.0, min_instrumentalness=SPOTIFY_MIN_INSTRUMENTALNESS,
			target_energy=0.5, target_valence = ((SENTIMENT_MIN_MAGNITUDE+0.01)+1.0)/2.0)
		.returns({
				'tracks' : [ {
					'external_urls' : {
						'spotify' : fake_spotify_url
					}
				}]
			}))

	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json[RESPONSE_KEY_POETRY] == '\n'.join([fake_poetry_line for _ in range(POEM_LINES_TO_GENERATE)])
	assert response_json[RESPONSE_KEY_TWEETS_READ_COUNT] == 1
	assert response_json[RESPONSE_KEY_AVG_SENTIMENT] == SENTIMENT_MIN_MAGNITUDE + 0.01
	assert response_json[RESPONSE_KEY_TRACK] == fake_spotify_url

	# Set MIN_TWEETS_TO_READ and MAX_TWEETS_TO_READ back to normal
	geo_poetry_server.MIN_TWEETS_TO_READ = prev_min_tweets
	geo_poetry_server.MAX_TWEETS_TO_READ = prev_max_tweets

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator', 
	'vaderSentiment.vaderSentiment.sentiment', 'spotipy.oauth2.SpotifyClientCredentials',
	'spotipy.Spotify')
def test_get_geo_poetry_min_sentiment_magnitude(MockGeoTweets, MockMarkovGenerator, MockGetSentiment, MockClientCredentials, MockSpotify):
	"""
	The get_geo_poetry method excludes sentiments with absolute value less than SENTIMENT_MIN_MAGNITUDE from the average sentiment.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	# Temporarily set low enough minimum number of tweets to read
	prev_min_tweets = geo_poetry_server.MIN_TWEETS_TO_READ
	geo_poetry_server.MIN_TWEETS_TO_READ = 0
	fake_tweets_list = iter(['Tweet 1', 'Tweet 2'])
	fake_poetry_line = 'A Line Of CG Poetry.'
	fake_spotify_url = 'http://www.example.com'
	def check_location_obj(obj):
		if not isinstance(obj, Location):
			return False
		if not obj.latitude == 0.0:
			return False
		if not obj.longitude == 0.0:
			return False
		if not obj.radius == 10:
			return False
		if not obj.imperial_units == True:
			return False
		return True
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.returns_fake()
		.expects('Tweets').with_args(arg.passes_test(check_location_obj))
		.returns(fake_tweets_list))
	(MockMarkovGenerator.expects_call()
		.with_args(['Tweet 1', 'Tweet 2'], MARKOV_DEPTH, ':memory:')
		.returns_fake()
		.expects('next').times_called(POEM_LINES_TO_GENERATE).returns(fake_poetry_line))
	(MockGetSentiment.expects_call()
		.with_args('Tweet 1')
		.returns({'compound': SENTIMENT_MIN_MAGNITUDE + 0.01})
		.next_call().with_args('Tweet 2')
		.returns({'compound': SENTIMENT_MIN_MAGNITUDE - 0.01}))
	(MockClientCredentials.expects_call()
		.with_args(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
		.returns('Constant'))
	(MockSpotify.expects_call()
		.with_args(client_credentials_manager='Constant')
		.returns_fake()
		.expects('recommendations').with_args(
			seed_genres = [SPOTIFY_DEFAULT_GENRE],
			limit=1, target_instrumentalness=1.0, min_instrumentalness=SPOTIFY_MIN_INSTRUMENTALNESS,
			target_energy=0.5, target_valence = ((SENTIMENT_MIN_MAGNITUDE+0.01)+1.0)/2.0)
		.returns({
				'tracks' : [ {
					'external_urls' : {
						'spotify' : fake_spotify_url
					}
				}]
			}))

	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json[RESPONSE_KEY_POETRY] == '\n'.join([fake_poetry_line for _ in range(POEM_LINES_TO_GENERATE)])
	assert response_json[RESPONSE_KEY_TWEETS_READ_COUNT] == 2
	assert response_json[RESPONSE_KEY_AVG_SENTIMENT] == SENTIMENT_MIN_MAGNITUDE + 0.01
	assert response_json[RESPONSE_KEY_TRACK] == fake_spotify_url

	# Set MIN_TWEETS_TO_READ back to normal
	geo_poetry_server.MIN_TWEETS_TO_READ = prev_min_tweets

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator', 
	'vaderSentiment.vaderSentiment.sentiment', 'spotipy.oauth2.SpotifyClientCredentials',
	'spotipy.Spotify')
def test_get_geo_poetry_unknown_genre(MockGeoTweets, MockMarkovGenerator, MockGetSentiment, MockClientCredentials, MockSpotify):
	"""
	The get_geo_poetry method returns 400 Bad Request when Spotify returns no tracks.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	# Temporarily set low enough minimum number of tweets to read
	prev_min_tweets = geo_poetry_server.MIN_TWEETS_TO_READ
	geo_poetry_server.MIN_TWEETS_TO_READ = 0
	fake_tweets_list = iter(['Tweet 1', 'Tweet 2'])
	fake_poetry_line = 'A Line Of CG Poetry.'
	fake_spotify_url = 'http://www.example.com'
	fake_genre = 'MyGenre'
	def check_location_obj(obj):
		if not isinstance(obj, Location):
			return False
		if not obj.latitude == 0.0:
			return False
		if not obj.longitude == 0.0:
			return False
		if not obj.radius == 10:
			return False
		if not obj.imperial_units == True:
			return False
		return True
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.returns_fake()
		.expects('Tweets').with_args(arg.passes_test(check_location_obj))
		.returns(fake_tweets_list))
	(MockMarkovGenerator.expects_call()
		.with_args(['Tweet 1', 'Tweet 2'], MARKOV_DEPTH, ':memory:')
		.returns_fake()
		.expects('next').times_called(POEM_LINES_TO_GENERATE).returns(fake_poetry_line))
	(MockGetSentiment.expects_call()
		.with_args('Tweet 1')
		.returns({'compound': SENTIMENT_MIN_MAGNITUDE + 0.01})
		.next_call().with_args('Tweet 2')
		.returns({'compound': -(SENTIMENT_MIN_MAGNITUDE + 0.01)}))
	(MockClientCredentials.expects_call()
		.with_args(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
		.returns('Constant'))
	(MockSpotify.expects_call()
		.with_args(client_credentials_manager='Constant')
		.returns_fake()
		.expects('recommendations').with_args(
			seed_genres = [fake_genre],
			limit=1, target_instrumentalness=1.0, min_instrumentalness=SPOTIFY_MIN_INSTRUMENTALNESS,
			target_energy=0.5, target_valence = ((0.0)+1.0)/2.0)
		.returns({ 'tracks' : []}))

	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True,
			'genre' : fake_genre}),
		content_type='application/json')
	assert response.status_code == 400

	# Set MIN_TWEETS_TO_READ back to normal
	geo_poetry_server.MIN_TWEETS_TO_READ = prev_min_tweets


if __name__ == '__main__':
	# Run pytest on this file
	pytest.main([__file__])