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
from geo_twitter import GeoTweets, MIN_NUM_FOLLOWERS, MAX_NUM_FOLLOWERS
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
	GeoTweets constructor constructs a Twython instance.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
	"""
	(MockTwython.expects_call()
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake())
	GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)

@fudge.patch('twython.Twython')
def test_GeoTweets_FetchTweets_imperial(MockTwython):
	"""
	GeoTweets.FetchTweets calls Twython API correctly for imperial units.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.FetchTweets}
	"""
	tweets_page1 = {
		'statuses' : [
			{
				'id' : 'status1'
			},
			{
				'id' : 'status2'
			}
		]
	}
	tweets_page2 = {
		'statuses' : [
			{
				'id' : 'status2'
			},
			{
				'id' : 'status3'
			}
		]
	}
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()

				# FetchTweets
				.expects('search').with_args(q='-RT', result_type='recent',
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'mi')
				.returns(tweets_page1)
				.expects('search').with_args(q='-RT', result_type='recent', max_id='status2',
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'mi')
				.returns(tweets_page2)
				.expects('search').with_args(q='-RT', result_type='recent',  max_id='status3',
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'mi')
				.returns(None)) #Returning None will cause the generator to stop
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	fake_location = Location(FAKE_LOCATION_LAT, FAKE_LOCATION_LONG, FAKE_LOCATION_RADIUS, True)
	tweets = [tweet for tweet in geo_tweets.FetchTweets(fake_location)]
	assert len(tweets) == 3
	assert tweets[0]['id'] == 'status1'
	assert tweets[1]['id'] == 'status2'
	assert tweets[2]['id'] == 'status3'

@fudge.patch('twython.Twython')
def test_GeoTweets_FetchTweets_metric(MockTwython):
	"""
	GeoTweets.FetchTweets calls Twython API correctly for metric units.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.FetchTweets}
	"""
	tweets_page1 = {
		'statuses' : [
			{
				'id' : 'status1'
			},
			{
				'id' : 'status2'
			}
		]
	}
	tweets_page2 = {
		'statuses' : [
			{
				'id' : 'status2'
			},
			{
				'id' : 'status3'
			}
		]
	}
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake()

				# FetchTweets
				.expects('search').with_args(q='-RT', result_type='recent',
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'km')
				.returns(tweets_page1)
				.expects('search').with_args(q='-RT', result_type='recent', max_id='status2',
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'km')
				.returns(tweets_page2)
				.expects('search').with_args(q='-RT', result_type='recent', max_id='status3',
									geocode=str(FAKE_LOCATION_LAT)+','+str(FAKE_LOCATION_LONG)+','+str(FAKE_LOCATION_RADIUS)+'km')
				.returns(None)) #Returning None will cause the generator to stop
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	fake_location = Location(FAKE_LOCATION_LAT, FAKE_LOCATION_LONG, FAKE_LOCATION_RADIUS, False)
	tweets = [tweet for tweet in geo_tweets.FetchTweets(fake_location)]
	assert len(tweets) == 3
	assert tweets[0]['id'] == 'status1'
	assert tweets[1]['id'] == 'status2'
	assert tweets[2]['id'] == 'status3'

@fudge.patch('twython.Twython')
def test_GeoTweets_CleanTweets(MockTwython):
	"""
	GeoTweets.CleanTweets removes urls, hashtags, @mentions, and skips tweets that are empty after cleaning.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.CleanTweets}
	"""
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake())
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
	dirty_tweet = "  http://www.google.com/ @some_username hello, world #uggghhhh  "
	url_tweet = "http://example.com/my%20webpage"
	clean_tweet = "hello, world"
	cleaned = [x for x in geo_tweets.CleanTweets([dirty_tweet, url_tweet])]
	assert len(cleaned) == 1
	assert cleaned[0] == clean_tweet

@fudge.patch('twython.Twython')
def test_GeoTweets_FilterTweets(MockTwython):
	"""
	GeoTweets.FilterTweets filters out tweets from verified users or users with too many or too few followers.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.FilterTweets}
	"""
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake())
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)

	tweet_verified_user = {
		'user' : {
			'verified' : True,
			'followers_count' : MIN_NUM_FOLLOWERS
		}
	}
	tweet_too_few_followers = {
		'user' : {
			'verified' : False,
			'followers_count' : MIN_NUM_FOLLOWERS - 1
		}
	}
	tweet_too_many_followers = {
		'user' : {
			'verified' : False,
			'followers_count' : MAX_NUM_FOLLOWERS + 1
		}
	}
	tweet_okay = {
		'user' : {
			'verified' : False,
			'followers_count' : MIN_NUM_FOLLOWERS
		}
	}
	tweets = [tweet_verified_user, tweet_okay, tweet_too_many_followers, tweet_too_few_followers]
	filtered_tweets = [tweet for tweet in geo_tweets.FilterTweets(tweets)]
	assert len(filtered_tweets) == 1
	assert filtered_tweets[0] == tweet_okay

@fudge.patch('twython.Twython')
def test_GeoTweets_ExtractText(MockTwython):
	"""
	GeoTweets.FilterTweets filters out tweets from verified users or users with too many or too few followers.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.FilterTweets}
	"""
	(MockTwython.expects_call()
				# __init__
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)
				.returns_fake())
	geo_tweets = GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET)

	tweets = [{ 'text' : 'Text1' }, { 'text' : 'Text2' }]
	assert [s for s in geo_tweets.ExtractText(tweets)] == ['Text1', 'Text2']


if __name__ == '__main__':
	pytest.main([__file__])