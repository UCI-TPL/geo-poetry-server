"""
Unit tests for module L{geo_poetry_server}
"""
import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

import pytest
from geo_poetry_server import app, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from geo_poetry_server import MARKOV_DEPTH, POEM_LINES_TO_GENERATE, RESPONSE_KEY_POETRY
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

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator')
def test_get_geo_poetry(MockGeoTweets, MockMarkovGenerator):
	"""
	The get_geo_poetry method works as expected when given valid input.

	Functions tested:
		- L{geo_poetry_server.get_geo_poetry}
	"""
	fake_tweets_list = ['ListOfTweets']
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
	(MockMarkovGenerator.expects_call()
		.with_args(arg.any(), MARKOV_DEPTH, ':memory:')
		.returns_fake()
		.expects('next').times_called(POEM_LINES_TO_GENERATE).returns(fake_poetry_line))

	response = client.post("/geo-poetry", data=json.dumps({
			'latitude' : 0.0,
			'longitude' : 0.0,
			'radius' : 10,
			'imperial_units' : True}),
		content_type='application/json')
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json[RESPONSE_KEY_POETRY] == '\n'.join([fake_poetry_line for _ in range(POEM_LINES_TO_GENERATE)])


if __name__ == '__main__':
	# Run pytest on this file
	pytest.main([__file__])