import os
from datetime import datetime 
from collections import OrderedDict
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils.database_utilities import Database
from utils.product_recommendation import (get_index_and_value,
                                          read_default_values)
from utils.utilities import *

app = Flask(__name__)

CORS(app)


DB_URL = "mongodb://localhost:27017/"
DB_NAME = "tvs"
questions_collection = 'questions'
options_collection = 'options'




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
    payload = request.get_json(force=True)
    db = Database(db_url=DB_URL,db_name=DB_NAME, collection_name=questions_collection)
    if db.connect_to_collection().find_one( {"_id" : payload['_id']}) is None:
        db.insert_documents(payload)
        return jsonify({"msg":"inserted","inserted_data":payload}),200
    else:
        return jsonify({"msg":"question number already exist"})



@app.route('/admin/edit_question',methods = ['PUT'])
@required_params(required=['_id'])
def edit_question():
    """takes 'option_number' and 'value' as payload to edit option else send the 'question' with proper '_id' to edit

    Returns:
         success or failure message
    """
    payload = request.get_json(force=True)
    db = Database(db_url=DB_URL,db_name=DB_NAME, collection_name=questions_collection)
    record = db.connect_to_collection().find_one( {"_id" : payload['_id']})
    if record is not None :
        if 'option_number'  in payload and 'value'  in payload :
            current_options = record['options']
            option_number = payload['option_number']
            #update the option with new value and remove the edits to update the payload data as document
            current_options[option_number] =  payload['value']
            del payload['option_number']
            del payload['value']
            payload['options'] = current_options
        db.connect_to_collection().update_one({"_id" : payload['_id']},{"$set":payload})
        print("Payload:: ",payload)
        return jsonify({"msg":"options updated"}),200
    return jsonify({"msg":"invalid question number..."}),400

@app.route('/admin/create_options',methods=['POST'])
@required_params(required=['_id',"option_number","filters_values"])
def create_options():
    ##expecting payload filter names as json object for now
    ##might need to change the functionality later
    payload = request.get_json(force=True)
    db = Database(db_url=DB_URL,db_name=DB_NAME, collection_name=options_collection)
    record = db.connect_to_collection().find_one( {"_id" : payload['_id']})
    payload['filters_values'] = OrderedDict(sorted(payload['filters_values'].items()))

    if record is None:
        filters_affected = list(payload['filters_values'].keys())
        dictionary_of_filter_values = read_default_values()
        indexes = []
        for filter in filters_affected:
            index,_ = get_index_and_value(dictionary_of_filter_values,filter)
            indexes.append(index)
        resp = {
            "_id": payload["_id"],
            "index_values":indexes
        }
        db.insert_documents(resp)
    values = list(payload['filters_values'].values())
    resp = {
        payload['option_number']:values
    }
    db.connect_to_collection().update_one({"_id" : payload['_id']},{"$set":resp})

    return jsonify({'indexes':resp}),200


@app.route('/admin/show_features',methods = ['GET'])
def show_features():
        dictionary_of_filter_values = read_default_values()
        return jsonify({'features':list(dictionary_of_filter_values.keys())})


@app.route('/admin/edit_options',methods = ['POST'])
def edit_options():
    pass



ALLOWED_EXTENSIONS = set(['csv'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
import pandas as pd 
@app.route('/admin/upload',methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        
        filename = secure_filename(file.filename)
        new_filename = f'{filename.split(".")[0]}.csv'
        save_location = os.path.join('admin','uploaded_files', new_filename)
        file.save(save_location)
        df = pd.read_csv(save_location)
        columns_in_data = list(df.columns)
        columns_in_data = [i for i in columns_in_data if not i.startswith('Unnamed')and i]
        # return columns_in_data
        
        #return send_from_directory('output', output_file)
        
        return jsonify({'msg':'Thanks for uploading','columns':columns_in_data})
    return jsonify({'msg':'Attach the csv file.'})

    

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
