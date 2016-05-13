from twython import Twython
from types import *

class GeoTweets:
	"""Fetches recent tweets from the area surrounding a particular GPS location.
	Constructor may throw TwythonAuthError."""

	def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
		self.api = Twython(consumer_key, consumer_secret, access_token_key, access_token_secret)
		self.api.verify_credentials()
	
	def FilterTweets(self, list):
		"""Generator that attempts to eliminate commercial tweets."""
		# TODO Use Bayesian spam filtering? This is gonna be tricky...
		for item in list:
			yield item

	def CleanTweets(self, list):
		"""Generator that removes unwanted text (URLs, #tags, @mentions) from tweets."""
		for tweet in list:
			tweet_clean = re.sub(URL_REGEX, '', s) # Remove URLs
			tweet_clean = re.sub(r'@\w+', '', s_clean) # Remove mentions
			tweet_clean = re.sub(r'#\w+', '', s_clean) # Remove hashtags
			tweet_clean = tweet_clean.trim() # Trim whitespace
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
		return twitter.cursor(twitter.search, q='-RT', result_type='recent', lang='en', geocode=location_str)

	def tweets(self, location):
		"""Generator that queries the Twitter API to fetch nearby tweets, and filters and cleans them."""
		return self.CleanTweets(self.FilterTweets(self.FetchTweets(location)))