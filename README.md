Geo-Poetry Server
=================

This is the server for the Geo-Poetry E-literature system. The system produces 
crowd-sourced, computer-generated poetry and mood music for the user's 
current location.


System Requirements
-------------------
* **Python 2.7** [https://www.python.org/](https://www.python.org/)
* **Flask**, a web microframework for Python [http://flask.pocoo.org/](http://flask.pocoo.org/)
* **Flask-CORS**, a Flask extension adding support for Cross-Origin Resource Sharing [https://github.com/corydolphin/flask-cors](https://github.com/corydolphin/flask-cors)
* **Twython**, a Python wrapper for the Twitter API [https://github.com/ryanmcgrath/twython](https://github.com/ryanmcgrath/twython)
* **Spotipy**, a Python wrapper for the Spotify API [https://github.com/plamere/spotipy](https://github.com/plamere/spotipy)

Unit tests also require:
* **pytest**, a testing framework [http://pytest.org/](http://pytest.org/)
* **fudge**, a mocking/stubbing framework [http://farmdev.com/projects/fudge/](http://farmdev.com/projects/fudge/)

All of the Python modules are also available directly through PIP, the Python 
package management system [https://pypi.python.org/pypi/pip](https://pypi.python.org/pypi/pip).


Credits
-------

In addition to the packages listed in the system requirements, Geo-Poetry 
uses modified versions of the following open-source projects:
* **markov-text**, a Python markov-chain text generator tool [https://github.com/codebox/markov-text](https://github.com/codebox/markov-text). It was modified to an externally usable package (it was only usable as a command-line utility), and some changes were made to how it splits words, in order to support contractions and abbreviations.
* **VADER-Sentiment-Analysis**, a Python sentiment analysis tool [https://github.com/cjhutto/vaderSentiment](https://github.com/cjhutto/vaderSentiment). It was modified to support unicode.


Client Usage
------------

The server exposes an API with two methods.

1. **/ping (GET)** - This method allows clients to check if the server is up.
	It returns a JSON object with two fields:

	* "up" - will always be <code>true</code>
	* "version" - the current version of the server, as a string (e.g. "0.1")

2. **/geo-poetry (POST)** - This is the method for fetching poetry and mood music.
	It accepts JSON with the following attributes:

	* "latitude" - *Required.* The GPS latitude coordinate, as a floating-point number or a string.
	* "longitude" - *Required.* The GPS longitude coordinate, as a floating-point number or a string.
	* "radius" - *Optional.* The radius within which to search, as a number or a string. The default is 10km.
	* "imperial_units" - *Optional.* A boolean - if true, use miles for the radius; if false, use kilometers.
	* "genre" - *Optional.* A string specifying the genre of music to select from. The default is "ambient". Use the */get-genres* method to get a list of available genres.
	* "song_energy" - *Optional.* A floating-point number between 0 and 1 specifying the energeticness of the track to return. Allows clients to vary the music energy over time.

	POST data must be sent with the *application/json* mime-type. For security
	of the transmitted GPS coordinates, HTTPS is required. It returns JSON with
	the following attributes:

	* "poetry" - A string of computer-generated poetry.
	* "track" - A Spotify URI for the mood music to play. (See the definition of Spotify URI at the Spotify API: [https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids](https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids))
	* "num_source_tweets" - An integer specifying how many tweets were read. Excludes those tweets that were filtered out as potential marketing or corporate tweets. See the algorithm description.
	* "genre" - The genre that the track was selected from. If the genre argument was given, the value will be identical.
	* "sentiment" - The valence that was computed and used to select mood music. Ranges from -1 to 1.

3. **/get-genres (GET)** - This method gives clients a list of the available genres for selecting music in.
	It returns a JSON object with one field:

	* "genres" - A list of strings, each of which is a valid argument to the "genre" parameter of the */geo-poetry* method.


Algorithm Description
---------------------

Each request to generate location-linked poetry requires 5 parameters: `latitude`, `longitude`, `radius`, `genre`, and `energy`. First, the Twitter API is queried for tweets that are geotagged within the radius of the specified latitude and longitude. Some simple filtering is applied in an attempt to exclude marketing and promotional tweets. In particular, we exclude retweets, tweets from "verified" accounts, and tweets from accounts with more than 10,000 followers. The tweet text is cleaned of URLs, hashtags, and “@mentions.” The resulting corpus of text is fed into a Markov-chain text generator, which generates a few lines of “poetry” that are, statistically speaking, similar to what people in the area are saying on Twitter – albeit largely nonsensical.

Next, this same corpus of text is given to the `VADER-sentiment-analysis` library. Sentiment analysis yields a parameter called the valence, which ranges from `-1` (extremely negative affect) to `1` (extremely positive affect), and can be any number in between. Spotify's music recommendation API requires at least one seed, which can be a genre, track, or artist. We use a seed genre, which may be selected by the user but defaults to “ambient.” In addition to the genre, we specify three parameters for Spotify's API: `valence`, given by our sentiment analysis; `energy`, a measure of activity and intensity; and `instrumentalness`, which we always set to its maximum value – because the design vision is for background music during a road trip, fully instrumental music is preferred. The Spotify API returns a track ID, which the web frontend uses to display a playable Spotify widget alongside the generated lines of poetry. (For the current code of the web frontend, see the [geo-poetry-demo project](https://github.com/UCI-TPL/geo-poetry-demo). The long-term vision is to develop a mobile application that will connect to the same backend.)

Sentiment analysis is applied to each tweet individually, and the resulting valence measure is averaged across all tweets read. At such a large scale, the valence falls prey to the law of averages – average valence tends towards neutral (zero). In an attempt to mitigate this problem, we exclude relatively neutral tweets from the average. We consider tweets to be “relatively neutral” if their valence fell within a certain interval centered around zero – in particular, plus or minus 0.2 (see the Configuration Constants section below on how to change this interval).

`Valence` and `energy` together describe the mood that the music track seeks to capture and convey. However, sentiment analysis only yields one dimension of affect, which is converted into the `valence` parameter. Thus, `energy` is specified by the client, which varies energy between requests according to a simple sine wave. Future versions of the work could vary energy according to some narrative or affective arc, building up and then releasing tension.

Setup and Development Guide
------------------------

### Configuration File

For security purposes, API keys and secrets are not stored anywhere in the Git repository. Instead, they are stored in a configuration file that is excluded from Git. The file is in the standard `.conf` file format. It should be located at `/conf/server.conf`. Here is an example file:

	[Twitter]
	consumer_key=XXXXXXXXXXXX
	consumer_secret=XXXXXXXXXX
	access_token_key=XXXXX-XXXXXXXXXXXXXXX
	access_token_secret=XXXXXXXXXXXXXXX

	[Spotify]
	client_id=XXXXXXXXXXXXXXXXXXXXXXXX
	client_secret=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

You will need to register the application with Twitter and with Spotify. Follow their documentation on how to obtain the API keys and secrets. For the Spotify API, it is recommended to create a new Spotify account for use only with this application, as the user's individual music history seems to bias Spotify's recommendation API. A new account that has never played any songs will, in theory, avoid this bias.

### Running the Server

1. Make sure all the system requirements are fulfilled.
2. Clone the repository somewhere on your server.
3. Create and fill in the configuration file as described above.
4. Run `geo_poetry_server.py`. If you have Python 3 installed on your system as well, make sure you run the script with Python 2.7.
5. The server is now listening on port 5000. If you need a different port number, check the Flask documentation and make appropriate code changes.

### Running Unit Tests

Unit tests are separated into two directories. First, there are the main unit tests, located under the `/test` directory at the root of the repository. These are the only ones that will be relevant for most development purposes. They can be run directly as Python scripts, but you will need the `fudge` and `pytest` packages installed. The script `/test/test_template.py` is not a unit test. Rather, it is a template for the creation of future unit tests.

Second, the `markov_text` package has its own unit tests, which have been modified to work with the changes made to the package. They are located at `/markov_text/test`. They use Python's built-in `unittest` package, and so do not require any additional packages to run.

### Configuration Constants

Various implementation details are stored as Python variables and are easy to change. They will be located at the beginning of the relevant Python file and will be named in all caps. They are all described in the table below. Most are located in the main server script, `geo_poetry_server.py`.

<table>
	<thead>
		<th>File</th>
		<th>Constant Name</th>
		<th>Value</th>
		<th>Description</th>
	</thead>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>VERSION</td>
		<td>"0.0"</td>
		<td>The server version.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>CONF_FILE_PATH</td>
		<td>"conf/server.conf"</td>
		<td>The path to look for a `.conf` file containing API keys.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>RESPONSE_KEY_POETRY</td>
		<td>"poetry"</td>
		<td>The JSON attribute under which the poetry text is stored in the response.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>RESPONSE_KEY_TWEETS_READ_COUNT</td>
		<td>"num_source_tweets"</td>
		<td>The JSON attribute under which the number of tweets read is stored in the response.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>RESPONSE_KEY_AVG_SENTIMENT</td>
		<td>"sentiment"</td>
		<td>The JSON attribute under which the average tweet sentiment is stored in the response.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>RESPONSE_KEY_TRACK</td>
		<td>"track"</td>
		<td>The JSON attribute under which the Spotify ID of the recommended track is stored in the response.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>RESPONSE_KEY_GENRE</td>
		<td>"genre"</td>
		<td>The JSON attribute under which the Spotify seed genre is stored in the response.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>MAX_TWEETS_TO_READ</td>
		<td>500</td>
		<td>The algorithm will read at least MIN_TWEETS_TO_READ and at most MAX_TWEETS_TO_READ tweets, excluding those filtered out. If it hits Twitter's API rate limit before reading MIN_TWEETS_TO_READ tweets, it will return HTTP 429: Too Many Requests.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>MIN_TWEETS_TO_READ</td>
		<td>100</td>
		<td>The algorithm will read at least MIN_TWEETS_TO_READ and at most MAX_TWEETS_TO_READ tweets, excluding those filtered out. If it hits Twitter's API rate limit before reading MIN_TWEETS_TO_READ tweets, it will return HTTP 429: Too Many Requests.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>MARKOV_DEPTH</td>
		<td>2</td>
		<td>The size of the n-grams to examine for Markov-chain text generation. With this scale of a corpus, we have found 2 to be a good number - it is the minimum for the generator to work, but setting the depth to 3 tends to regurgitate tweets verbatim, with no scrambling.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>POEM_LINES_TO_GENERATE</td>
		<td>3</td>
		<td>The number of lines of poetry to generate.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>DEFAULT_RADIUS</td>
		<td>10</td>
		<td>The radius defaults to 10km if not specified by the client.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>DEFAULT_IMPERIAL_UNITS</td>
		<td>False</td>
		<td>The radius defaults to 10km if not specified by the client.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>SENTIMENT_MIN_MAGNITUDE</td>
		<td>0.2</td>
		<td>In an attempt to avoid relatively neutral results, tweets with a sentiment within this number of zero will be excluded from the average sentiment calculation. See the algorithm description.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>SPOTIFY_DEFAULT_GENRE</td>
		<td>"ambient"</td>
		<td>The seed genre will default to this value if not specified by the client.</td>
	</tr>
	<tr>
		<td>/geo_poetry_server.py</td>
		<td>SPOTIFY_DEFAULT_ENERGY</td>
		<td>0.5</td>
		<td>The song energy will default to this value if not specified by the client.</td>
	</tr>
	<tr>
		<td>/geo_twitter.py</td>
		<td>URL_REGEX</td>
		<td>r'(https?://\S*)'</td>
		<td>The regular expression used to match URLs in order to clean them from tweets.</td>
	</tr>
	<tr>
		<td>/geo_twitter.py</td>
		<td>MIN_NUM_FOLLOWERS</td>
		<td>0</td>
		<td>Tweets from accounts with less than this many followers will be filtered out.</td>
	</tr>
	<tr>
		<td>/geo_twitter.py</td>
		<td>MAX_NUM_FOLLOWERS</td>
		<td>10000</td>
		<td>Tweets from accounts with more than this many followers will be filtered out.</td>
	</tr>
</table>