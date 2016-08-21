"""
The geo_twitter module exports a single class, L{GeoTweets}, that handles fetching tweets near a location.
"""
import twython
import re
from common_types import *

URL_REGEX = r'(https?://\S*)' # Eh, good enough for my purposes
MIN_NUM_FOLLOWERS = 0
MAX_NUM_FOLLOWERS = 10000

import os.path
import codecs
import datetime
TWEET_LOG_TEMPLATE = "%Y-%m-%d_%H-%M-%S.%f"
TWEET_LOG_EXT_UNFILTERED = "_unfiltered"
TWEET_LOG_EXT_FILTERED = "_filtered"
TWEET_LOG_EXT_CLEANED = "_cleaned"
TWEET_LOG_DIRECTORY = "logs/"

def asciify(string):
	"""Generator that removes non-ASCII characters and newlines from a string."""
	for ch in string:
		if (ord(ch) <= 127) and (ch != '\n'):
			yield ch
		else:
			continue

class GeoTweets:
	"""Fetches recent tweets from the area surrounding a particular GPS location.
	Methods may throw TwythonAuthError."""

	def __init__(self, consumer_key, consumer_secret):
		self.api = twython.Twython(consumer_key, consumer_secret)
		self.tweet_log_unfiltered = None
		self.tweet_log_filtered = None
		self.tweet_log_cleaned = None

	def FilterTweets(self, list):
		"""Generator that attempts to eliminate commercial tweets.
		Filters out tweets from (1) verified accounts, and
			(2) Accounts with less than MIN_NUM_FOLLOWERS or greater than MAX_NUM_FOLLOWERS followers."""
		for tweet in list:
			if self.tweet_log_unfiltered:
				self.tweet_log_unfiltered.write(u"[{}] {}\n".format(tweet['user']['name'], tweet['text']))
			if tweet['user']['verified']:
				continue
			elif tweet['user']['followers_count'] < MIN_NUM_FOLLOWERS or tweet['user']['followers_count'] > MAX_NUM_FOLLOWERS:
				continue
			if self.tweet_log_filtered:
				self.tweet_log_filtered.write(u"[{}] {}\n".format(tweet['user']['name'], tweet['text']))
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
				if self.tweet_log_cleaned:
					self.tweet_log_cleaned.write(u"{}\n".format(tweet_clean))
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
		max_id = None
		while True:
			if max_id:
				response = self.api.search(q='-RT', result_type='recent', geocode=location_str, max_id=max_id)
				if not response:
					raise StopIteration
				# max_id is inclusive, so the last tweet from the previous page will be repeated, so we skip it
				for status in response['statuses'][1:]:
					yield status
				max_id = response['statuses'][-1]['id']
			else: # first iteration
				response = self.api.search(q='-RT', result_type='recent', geocode=location_str)
				if not response:
					raise StopIteration
				for status in response['statuses']:
					yield status
				max_id = response['statuses'][-1]['id']

	def Tweets(self, location, log_tweets = False):
		"""Generator that queries the Twitter API to fetch nearby tweets, and filters and cleans them.

		Simply chains all the generator methods: L{FetchTweets} -> L{FilterTweets} -> L{ExtractText} -> L{CleanTweets}
		Because this is all it does, I didn't bother including it in the unit tests."""
		if log_tweets:
			tweet_log_base = datetime.datetime.now().strftime(TWEET_LOG_TEMPLATE)
			self.tweet_log_unfiltered = codecs.open(os.path.join(TWEET_LOG_DIRECTORY, tweet_log_base+TWEET_LOG_EXT_UNFILTERED), 'w', 'utf-8')
			self.tweet_log_filtered = codecs.open(os.path.join(TWEET_LOG_DIRECTORY, tweet_log_base+TWEET_LOG_EXT_FILTERED), 'w', 'utf-8')
			self.tweet_log_cleaned = codecs.open(os.path.join(TWEET_LOG_DIRECTORY, tweet_log_base+TWEET_LOG_EXT_CLEANED), 'w', 'utf-8')
		generator = self.CleanTweets(self.ExtractText(self.FilterTweets(self.FetchTweets(location))))
		try:
			while True:
				yield generator.next()
		except twython.TwythonRateLimitError:
			raise StopIteration
		finally:
			if log_tweets:
				self.tweet_log_unfiltered.close()
				self.tweet_log_unfiltered = None
				self.tweet_log_filtered.close()
				self.tweet_log_filtered = None
				self.tweet_log_cleaned.close()
				self.tweet_log_cleaned = None