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
	* "num_source_tweets" - An integer specifying how many tweets were read. See the algorithm description.
	* "genre" - The genre that the track was selected from. If the genre argument was given, the value will be identical.
	* "sentiment" - The valence that was computed and used to select mood music. Ranges from -1 to 1.

3. **/get-genres (GET)** - This method gives clients a list of the available genres for selecting music in.
	It returns a JSON object with one field:

	* "genres" - A list of strings, each of which is a valid argument to the "genre" parameter of the */geo-poetry* method.


Algorithm Description
---------------------

Each request to generate location-linked poetry requires 5 parameters: latitude, longitude, radius, genre, and energy. First, the Twitter API is queried for tweets that are geotagged within the radius of the specified latitude and longitude. Some simple filtering is applied in an attempt to exclude marketing and promotional tweets. In particular, we exclude retweets, tweets from "verified" accounts, and tweets from accounts with more than 10,000 followers. The tweet text is cleaned of URLs, hashtags, and “@mentions.” The resulting corpus of text is fed into a Markov-chain text generator, which generates a few lines of “poetry” that are, statistically speaking, similar to what people in the area are saying on Twitter – albeit largely nonsensical.

Next, this same corpus of text is fed into VADER-sentiment-analysis. Sentiment analysis yields a parameter called the valence, which ranges from -1 (extremely negative affect) to 1 (extremely positive affect), and can be any number in between. Spotify's music recommendation API requires at least one seed, which can be a genre, track, or artist. We use a seed genre, which may be selected by the user but defaults to “ambient.” In addition to the genre, we specify three parameters for Spotify's API: valence, given by our sentiment analysis; energy, a measure of activity and intensity; and instrumentalness, which we always set to its maximum value – because the design vision is for background music during a road trip, fully instrumental music is preferred. The Spotify API returns a track ID, which the web frontend uses to display a playable Spotify widget alongside the generated lines of poetry. (For the current code of the web frontend, see the [geo-poetry-demo project](https://github.com/UCI-TPL/geo-poetry-demo). The long-term vision is to develop a mobile application that will connect to the same backend.)

Valence and energy together describe the mood that the music track seeks to capture and convey. However, sentiment analysis only yields one dimension of affect, described as valence. Thus, energy is specified by the client, which varies energy between requests according to a simple sine wave. Future versions of the work could vary energy according to some narrative or affective arc, building up and then releasing tension.

Server Development Guide
------------------------
TODO Guidelines for further development/extension, including how to run unit tests, installation/setup, configuration files, configuration constants in Python modules, etc.