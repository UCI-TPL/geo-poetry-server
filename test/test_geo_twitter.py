"""
Unit tests for module L{geo_twitter}
"""
import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

import fudge
from geo_twitter import GeoTweets

FAKE_CONSUMER_KEY = 'consumerkey'
FAKE_CONSUMER_SECRET = 'consumersecret'
FAKE_ACCESS_TOKEN_KEY = 'accesstokenkey'
FAKE_ACCESS_TOKEN_SECRET = 'accesstokensecret'

@fudge.patch('twython.Twython')
def test_GeoTweets_init(MockTwython):
	"""
	GeoTweets constructor constructs a Twython instance, then verifies credentials.

	Functions tested:
		- L{geo_twitter.GeoTweets.__init__}
		- L{geo_twitter.GeoTweets.verify_credentials}
	"""
	(MockTwython.expects_call()
				.with_args(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET, FAKE_ACCESS_TOKEN_KEY, FAKE_ACCESS_TOKEN_SECRET)
				.returns_fake().expects('verify_credentials').with_arg_count(0))
	GeoTweets(FAKE_CONSUMER_KEY, FAKE_CONSUMER_SECRET, FAKE_ACCESS_TOKEN_KEY, FAKE_ACCESS_TOKEN_SECRET)

if __name__ == '__main__':
	import pytest
	pytest.main([__file__])