"""
Unit tests for module L{geo_twitter}
"""
import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

import fudge
from fudge.inspector import arg
from geo_twitter import GeoTweets
from twython import TwythonAuthError
from common_types import Location
import pytest

FAKE_CONSUMER_KEY = 'consumerkey'
FAKE_CONSUMER_SECRET = 'consumersecret'
FAKE_LOCATION_LAT = 10.0
FAKE_LOCATION_LONG = 10.0
FAKE_LOCATION_RADIUS = 10

@fudge.patch('twython.Twython')
def test_GeoTweets_init(MockTwython):
	"""
	GeoTweets constructor constructs a Twython instance, then verifies credentials.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
	"""
	(MockTwython.expects_call()
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()
				.expects('verify_credentials').with_arg_count(0))
	GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)

@fudge.patch('twython.Twython')
def test_GeoTweets_verify_credentials(MockTwython):
	"""
	GeoTweets.verify_credentials calls Twython.verify_credentials.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
	"""
	(MockTwython.expects_call()
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()
				.expects('verify_credentials').with_arg_count(0)
				.expects('verify_credentials').with_arg_count(0))
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	geo_tweets.verify_credentials()

@fudge.patch('twython.Twython')
def test_GeoTweets_init_bad_credentials(MockTwython):
	"""
	GeoTweets constructor raises TwythonAuthError when credentials are bad.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
	"""
	(MockTwython.expects_call()
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()
				.expects('verify_credentials').with_arg_count(0)
				.raises(TwythonAuthError("Example message.")))
	with pytest.raises(TwythonAuthError):
		geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)

@fudge.patch('twython.Twython')
def test_GeoTweets_FetchTweets_imperial(MockTwython):
	"""
	GeoTweets.FetchTweets calls Twython API correctly for imperial units.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
		- L{geo_twitter.GeoTweets.FetchTweets}
	"""
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()
				.expects('verify_credentials').with_arg_count(0)

				# FetchTweets
				.has_attr(search=None)
				.expects('cursor').with_args(None, q='-RT', result_type='recent', lang='en', 
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'mi'))
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	fake_location = Location(FAKE_LOCATION_LAT, FAKE_LOCATION_LONG, FAKE_LOCATION_RADIUS)
	geo_tweets.FetchTweets(fake_location)

@fudge.patch('twython.Twython')
def test_GeoTweets_FetchTweets_metric(MockTwython):
	"""
	GeoTweets.FetchTweets calls Twython API correctly for metric units.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
		- L{geo_twitter.GeoTweets.FetchTweets}
	"""
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()
				.expects('verify_credentials').with_arg_count(0)

				# FetchTweets
				.has_attr(search=None)
				.expects('cursor').with_args(None, q='-RT', result_type='recent', lang='en', 
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'km'))
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	fake_location = Location(FAKE_LOCATION_LAT, FAKE_LOCATION_LONG, FAKE_LOCATION_RADIUS, False)
	geo_tweets.FetchTweets(fake_location)

@fudge.patch('twython.Twython')
def test_GeoTweets_CleanTweets(MockTwython):
	"""
	GeoTweets.CleanTweets removes urls, hashtags, @mentions, and skips tweets that are empty after cleaning.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
		- L{geo_twitter.GeoTweets.CleanTweets}
	"""
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()
				.expects('verify_credentials').with_arg_count(0))
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	dirty_tweet = "  http://www.google.com/ @some_username hello, world #uggghhhh  "
	url_tweet = "http://example.com/my%20webpage"
	clean_tweet = "hello, world"
	cleaned = [x for x in geo_tweets.CleanTweets([dirty_tweet, url_tweet])]
	assert len(cleaned) == 1
	assert cleaned[0] == clean_tweet


if __name__ == '__main__':
	pytest.main([__file__])