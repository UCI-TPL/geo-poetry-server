import twitter

class InvalidCredentialsException(Exception):
	pass

class Location:
	def __init__(self, longitude=None, latitude=None, radius=10, units='km'):
		self.longitude = longitude
		self.latitude = latitude
		self.radius = radius
		self.units = units

class GeoTweets:
	"""Fetches recent tweets from the area surrounding a particular GPS location."""

	def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
		self.api = twitter.Api(consumer_key=consumer_key,
					consumer_secret=consumer_secret,
					access_token_key=access_token_key,
					access_token_secret=access_token_secret)
		if self.api.VerifyCredentials() == None:
			raise InvalidCredentialsException
	
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
			else:
				continue

	def FetchTweets(self, location):
		"""Generator that queries the Twitter API to fetch nearby tweets"""
		# TODO 
		return []

	def tweets(self, location):
		"""Generator that queries the Twitter API to fetch nearby tweets, and filters and cleans them."""
		return self.CleanTweets(self.FilterTweets(self.FetchTweets(location)))