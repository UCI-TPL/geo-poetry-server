import twython
import re
from common_types import *

URL_REGEX = r'(https?://\S*)' # Eh, good enough for my purposes

class GeoTweets:
	"""Fetches recent tweets from the area surrounding a particular GPS location.
	Methods may throw TwythonAuthError."""

	def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
		self.api = twython.Twython(consumer_key, consumer_secret, access_token_key, access_token_secret)
		self.verify_credentials()

	def verify_credentials(self):
		"""Throws TwythonAuthError unless all Twitter credentials are valid."""
		self.api.verify_credentials()

	def FilterTweets(self, list):
		"""Generator that attempts to eliminate commercial tweets."""
		# TODO Use Bayesian spam filtering? This is gonna be tricky...
		for item in list:
			yield item

	def CleanTweets(self, list):
		"""Generator that removes unwanted text (URLs, #tags, @mentions) from tweets."""
		for tweet in list:
			tweet_clean = re.sub(URL_REGEX, '', tweet) # Remove URLs
			tweet_clean = re.sub(r'@\w+', '', tweet_clean) # Remove mentions
			tweet_clean = re.sub(r'#\w+', '', tweet_clean) # Remove hashtags
			tweet_clean = tweet_clean.strip() # Trim whitespace
			if len(tweet_clean) > 0:
				yield tweet_clean
			else: # Skip tweets that are now empty
				continue

	def FetchTweets(self, location):
		"""Generator that queries the Twitter API to fetch nearby tweets"""
		location_str = str(location.latitude)+','+str(location.longitude)+','+str(location.radius)
		if location.imperial_units:
			location_str += 'mi'
		else:
			location_str += 'km'
		return self.api.cursor(self.api.search, q='-RT', result_type='recent', lang='en', geocode=location_str)

	def Tweets(self, location):
		"""Generator that queries the Twitter API to fetch nearby tweets, and filters and cleans them."""
		return self.CleanTweets(self.FilterTweets(self.FetchTweets(location)))