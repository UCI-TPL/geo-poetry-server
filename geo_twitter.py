"""
The geo_twitter module exports a single class, L{GeoTweets}, that handles fetching tweets near a location.
"""
import twython
import re
from common_types import *

URL_REGEX = r'(https?://\S*)' # Eh, good enough for my purposes
MIN_NUM_FOLLOWERS = 0
MAX_NUM_FOLLOWERS = 10000

class GeoTweets:
	"""Fetches recent tweets from the area surrounding a particular GPS location.
	Methods may throw TwythonAuthError."""

	def __init__(self, consumer_key, consumer_secret):
		self.api = twython.Twython(consumer_key, consumer_secret)

	def FilterTweets(self, list):
		"""Generator that attempts to eliminate commercial tweets.
		Filters out tweets from (1) verified accounts, and
			(2) Accounts with less than MIN_NUM_FOLLOWERS or greater than MAX_NUM_FOLLOWERS followers."""
		for tweet in list:
			if tweet['user']['verified']:
				continue
			elif tweet['user']['followers_count'] < MIN_NUM_FOLLOWERS or tweet['user']['followers_count'] > MAX_NUM_FOLLOWERS:
				continue
			yield tweet

	def ExtractText(self, list):
		"""Generator that returns the tweet text strings from a list of tweets."""
		for tweet in list:
			yield tweet['text']

	def CleanTweets(self, list):
		"""Generator that removes unwanted text (URLs, #tags, @mentions) from a list of strings."""
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
		"""Generator that queries the Twitter API to fetch nearby tweets."""
		location_str = str(location.latitude)+','+str(location.longitude)+','+str(location.radius)
		if location.imperial_units:
			location_str += 'mi'
		else:
			location_str += 'km'
		return self.api.cursor(self.api.search, q='-RT', result_type='recent', lang='en', geocode=location_str)

	def Tweets(self, location):
		"""Generator that queries the Twitter API to fetch nearby tweets, and filters and cleans them.

		Simply chains all the generator methods: L{FetchTweets} -> L{FilterTweets} -> L{ExtractText} -> L{CleanTweets}
		Because this is all it does, I didn't bother including it in the unit tests."""
		generator = self.CleanTweets(self.ExtractText(self.FilterTweets(self.FetchTweets(location))))
		try:
			while True:
				yield generator.next()
		except twython.TwythonRateLimitError:
			# TODO This is useful if we hit the rate limit in the middle of a request, but we should
			#  notify the client if we are rate-limited before we can gather hardly any tweets.
			raise StopIteration