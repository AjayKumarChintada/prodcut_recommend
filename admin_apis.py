import re
import flask
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.database_utilities import Database
from utils.product_recommendation import *
from functools import wraps
from utils.utilities import *

app = Flask(__name__)

CORS(app)


DB_URL = "mongodb://localhost:27017/"
DB_NAME = "tvs"


def required_params(required):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            _json = request.get_json()
            ## to check missing keys of json object
            missing = [r for r in required if r not in _json]
            if missing:
                response = {
                    "status": "error",
                    "message": "Request JSON is missing some required param key",
                    "missing": missing
                }
                return jsonify(response), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/')
def home():
    return jsonify({'msg': 'Welcome to the home page...'})


@app.route('/admin/add_question', methods=['POST'])
@required_params(required=['_id', 'question', 'options'])
def add_question():
    questions_collection = 'questions'
    payload = request.get_json(force=True)
    # return {'payload': payload} 
    db = Database(db_url=DB_URL,db_name=DB_NAME, collection_name=questions_collection)
    db.insert_documents(payload)
    return jsonify({"msg":"inserted"}),200





if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
