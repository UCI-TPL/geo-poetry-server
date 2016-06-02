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

Unit tests also require:
* **pytest**, a testing framework [http://pytest.org/](http://pytest.org/)
* **fudge**, a mocking/stubbing framework [http://farmdev.com/projects/fudge/](http://farmdev.com/projects/fudge/)

All of the Python modules are also available directly through PIP, the Python 
package management system [https://pypi.python.org/pypi/pip](https://pypi.python.org/pypi/pip).


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
	* "imperial_units" - *Optional* A boolean - if true, use miles for the radius; if false, use kilometers.

	POST data must be sent with the *application/json* mime-type. For security
	of the transmitted GPS coordinates, HTTPS is required. It returns JSON with
	the following attributes:

	* "poetry" - A string of computer-generated poetry.
	* "track" - A Spotify URL for the mood music to play. (See the definition of Spotify URL at the Spotify API: [https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids](https://developer.spotify.com/web-api/user-guide/#spotify-uris-and-ids))
	* "num_source_tweets" - An integer specifying how many tweets were read. See the algorithm description.


Algorithm Description
---------------------
TODO Describe, in general terms, how poetry is generated and how sentiment analysis and track selection is done.

Server Development Guide
------------------------
TODO Guidelines for further development/extension, including how to run unit tests, installation/setup, configuration files, configuration constants in Python modules, etc.