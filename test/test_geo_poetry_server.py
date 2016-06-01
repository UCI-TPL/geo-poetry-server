import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

import pytest
from geo_poetry_server import app, HEADER_KEY_ACCESS_TOKEN_KEY, HEADER_KEY_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from flask import json
import fudge
from twython import TwythonAuthError

# CONSTANTS
FAKE_CONSUMER_KEY = 'consumerkey'
FAKE_CONSUMER_SECRET = 'consumersecret'
FAKE_ACCESS_TOKEN_KEY = 'AccessTokenKey'
FAKE_ACCESS_TOKEN_SECRET = 'AccessTokenSecret'

# SETUP
app.config['TESTING'] = True
client = app.test_client()

def test_ping():
	response = client.get("/ping")
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json['up'] == True
	assert response_json['version'] == "0.0"

def test_get_geo_poetry_missing_headers():
	response = client.get("/geo-poetry")
	assert response.status_code == 403

@fudge.patch('geo_twitter.GeoTweets')
def test_get_geo_poetry_bad_access_tokens(MockGeoTweets):
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, FAKE_ACCESS_TOKEN_KEY, FAKE_ACCESS_TOKEN_SECRET)
		.raises(TwythonAuthError("Example message.")))
	response = client.get("/geo-poetry", headers = {
		HEADER_KEY_ACCESS_TOKEN_KEY: FAKE_ACCESS_TOKEN_KEY, HEADER_KEY_ACCESS_TOKEN_SECRET: FAKE_ACCESS_TOKEN_SECRET})
	assert response.status_code == 403


if __name__ == '__main__':
	# Run pytest on this file
	pytest.main([__file__])