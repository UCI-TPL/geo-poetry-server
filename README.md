Geo-Poetry Server
=================

This is the server for the Geo-Poetry E-literature system. The system produces 
crowd-sourced, computer-generated poetry and mood music for the user's 
current location.


System Requirements
-------------------
* **Python 2.7** [https://www.python.org/](https://www.python.org/)
* **Flask**, a web microframework for Python [http://flask.pocoo.org/](http://flask.pocoo.org/)
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

	POST data must be sent with the *application/json* mime-type. For security
	of the transmitted GPS coordinates, HTTPS is required. It returns JSON with
	the following attributes:

	* "poetry" - A string of computer-generated poetry.
	* "track" - A Spotify URL for the mood music to play. (See the definition of Spotify URL at the Spotify API: [https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids](https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids))
	* "num_source_tweets" - An integer specifying how many tweets were read. See the algorithm description.

3. **/get-genres (GET)** - This method gives clients a list of the available genres for selecting music in.
	It returns a JSON object with one field:

	* "genres" - A list of strings, each of which is a valid argument to the "genre" parameter of the */geo-poetry* method.


Algorithm Description
---------------------
TODO Describe, in general terms, how poetry is generated and how sentiment analysis and track selection is done.

Server Development Guide
------------------------
TODO Guidelines for further development/extension, including how to run unit tests, installation/setup, configuration files, configuration constants in Python modules, etc.