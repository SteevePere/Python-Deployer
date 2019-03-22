"""Says hello to the world"""

from flask import Flask, jsonify


app = Flask(__name__)


#HELLO WORLD ROUTE
@app.route('/hello', methods=['GET'])

def hello_world():
    """Says hello to the world"""

    hello = "Hello, World!"

    return(hello)


#ERROR ROUTE
@app.errorhandler(404)

def not_found(error):
	return jsonify({'code':404,'message': 'Not Found'}),404


#RUNNING APP
if (__name__ == "__main__"):
    app.run(host='0.0.0.0', port=5003)
