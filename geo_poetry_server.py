from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({'up': True, 'version': "0.0"})

if __name__ == "__main__":
	app.debug = True #TODO Do NOT use debug mode in production
	app.run()