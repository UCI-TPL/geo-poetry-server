import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

import pytest
from geo_poetry_server import app, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET
from flask import json
import fudge
from twython import TwythonAuthError

# SETUP
app.config['TESTING'] = True
client = app.test_client()

def test_ping():
	response = client.get("/ping")
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json['up'] == True
	assert response_json['version'] == "0.0"

@fudge.patch('geo_twitter.GeoTweets')
def test_get_geo_poetry_auth_failure(MockGeoTweets):
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.raises(TwythonAuthError("Example message.")))
	with pytest.raises(TwythonAuthError):
		response = client.get("/geo-poetry")


if __name__ == '__main__':
	# Run pytest on this file
	pytest.main([__file__])