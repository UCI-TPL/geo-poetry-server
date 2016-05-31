from flask import Flask, jsonify, request, abort

HEADER_KEY_ACCESS_TOKEN_KEY = "X-TwitterAuthAccessTokenKey"
HEADER_KEY_ACCESS_TOKEN_SECRET = "X-TwitterAuthAccessTokenSecret"
# TODO Read my Twitter keys (consumer_key, consumer_secret) from conf file


app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({'up': True, 'version': "0.0"})

@app.route("/geo-poetry")
def get_geo_poetry():
	# Handle headers (Twitter auth credentials)
	try:
		access_token_key = request.headers[HEADER_KEY_ACCESS_TOKEN_KEY]
		access_token_secret = request.headers[HEADER_KEY_ACCESS_TOKEN_SECRET]
	except KeyError:
		abort(403)

if __name__ == "__main__":
	app.debug = True #TODO Do NOT use debug mode in production
	app.run()