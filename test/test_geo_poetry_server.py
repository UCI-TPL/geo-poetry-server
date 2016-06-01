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

@fudge.patch('geo_twitter.GeoTweets', 'markov_text.MarkovGenerator')
def test_get_geo_poetry(MockGeoTweets, MockMarkovGenerator):
	fake_tweets_list = 'ListOfTweets'
	fake_poetry_line = 'A Line Of CG Poetry.'
	(MockGeoTweets.expects_call()
		.with_args(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
		.returns_fake()
		.expects('Tweets').with_arg_count(0)
		.returns(fake_tweets_list))
	(MockMarkovGenerator.expects_call()
		.with_args(fake_tweets_list, MARKOV_DEPTH, arg.any())
		.returns_fake()
		.expects('next').times_called(POEM_LINES_TO_GENERATE).returns(fake_poetry_line))

	response = client.get("/geo-poetry")
	response_json = json.loads(response.get_data())
	assert response.status_code == 200
	assert response_json[RESPONSE_KEY_POETRY] == '\n'.join([fake_poetry_line for _ in range(POEM_LINES_TO_GENERATE)])


if __name__ == '__main__':
	# Run pytest on this file
	pytest.main([__file__])