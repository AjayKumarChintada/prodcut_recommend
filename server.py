import flask
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import pandas as pd
from functools import wraps
from upload_data_to_elastic_search import upload_data_es
from utils.database_utilities import Database
from utils.product_recommendation import (cosine_in_elastic_search,
                                          get_index_and_value,
                                          read_default_values, update_vector)
from utils.utilities import *

app = Flask(__name__)

CORS(app)

config = read_default_values('config.json')
database_url = config['db_url']
database_name = config['db_name']

## upload data to elastic search 
upload_data_es()

##global dictionary to store sessions..
sessions = {}
 


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



@app.route("/laptop_recommendations/user_choices")
def get_first_question():
    collection_name = config['collection_name']
    db = Database(db_url=database_url,db_name=database_name,collection_name=collection_name)
    session_id = generate_uuid()
    #creating a dictionary for every user 
    sessions[session_id] = {}
    resp = db.get_question_with_id(0)
    resp['next_question_number'] = 1
    # resp['session'] = session_id
    return jsonify({'question_data':resp,'session': session_id})




@app.route("/laptop_recommendations/user_choices", methods=["POST"])
@required_params(required=['question_number','choice_number','session'])
def user_choices():
    """takes question number and choice number 

    Returns:
        json object: array of user vector already updated
    """
   
    data = request.get_json(force=True)
    question_number = data['question_number']
    choice_number = data['choice_number']
    collection_name = config['collection_name']
    db = Database(db_url=database_url,db_name=database_name,collection_name=collection_name)



    if 'session' in data and data['session'] in sessions:
        # print(sessions)
        session = sessions[data['session']]
        # print('session exist and ',session)
        questions_data = db.get_question_with_id(question_number+1)
        if not questions_data and question_number != db.get_last_record_id():
            return jsonify({"Error": "invalid question number..."}), 404

        ## database connection for options collection
        options_collection_db = Database(database_url,database_name,config['options_collection'])
        results = options_collection_db.get_question_with_id(id_val=question_number) 
        if not results:
                return jsonify("Invalid Choice chosen..."), 404

        ### when  admin implementation method function get_indexes_values_from_db(results,str(choice_number))-> indexes,values will be called  
        # indexes ,values = get_indexes_values_from_db(results,str(choice_number))
        indexes, values = results[str(choice_number)]
        filters = results['original_vals'][int(choice_number)]
        ## for first time user initializing default vector first
        default_median_dictionary = read_default_values()
        if 'default' not in session:
            vector = list(default_median_dictionary.values())
            session['default'] = vector

        ## logic to append filters to backend
        filter_objects = make_filter_object(filters)
        if 'filters' not in session:
            session['filters'] = filter_objects
        else:
            for filter_object in filter_objects:
                flag, _ = search_and_get_index(
                    session['filters'], filter_object)
                if not flag:
                    session['filters'].append(filter_object)
    
        # updating that default vector using payload
        session['default'] = update_vector(session['default'], indexes, values)
        # updating filters
        resp = cosine_in_elastic_search(
            'laptop_recommendations', session['default'], 10)

        resp = modify_response_laptop_data(resp,session['filters'])
        # condition to handle last question
        if question_number == db.get_last_record_id():
            return jsonify({
                'laptop_data': resp,
                'question_data': {"question": 'All questions done', 'options': [], 'next_question_number': -1},
                'filters': session['filters'],
            'session': data['session']}), 200

        # questions
        if questions_data:
            questions_data['next_question_number'] = question_number+1
            resp = {'laptop_data': resp,
                            "question_data": questions_data,
                            'filters': session['filters']
                            ,'session': data['session']}
            return jsonify(resp), 200
    return jsonify({"msg":"Invalid Session id "})



@app.route("/laptop_recommendations/min_max_filter_values", methods=["GET"])
def min_max_filter_value():
    #default_vector_values = read_default_values('default_vector_values.json')
    #collection_name = config['dataset_collection']
    filter_collection = config['min_max_filter']
    db_filter = Database(db_url=database_url,db_name=database_name,collection_name= filter_collection)
    cursor = db_filter.connect_to_collection().find({}, {'_id': False})
    json_Data = list(cursor)

    #filter_list = list(default_vector_values.keys())
    #filter_dict = {}
    #list_filter = []
    #for i in range(0,len(filter_list)):
    #    filter_dict = {'max_value': db_filter.min_max_value(filter_name=filter_list[i])[1], 
    #                                    'min_value':db_filter.min_max_value(filter_name=filter_list[i])[2],
    #                                    'filter': db_filter.min_max_value(filter_name=filter_list[i])[0],
    #                                    'data_type': 'Number'}
    #    list_filter.append(filter_dict)

    #brand_list = db_filter.distinct_non_numeric_values('brand')[1]
    #filter_name = db_filter.distinct_non_numeric_values('brand')[0]
    #filtername = db_filter.distinct_non_numeric_values('brand')[0]
    #type2 = db_filter.distinct_non_numeric_values('brand')[2]
    #filter_dict = {'filter':filter_name,'values':brand_list, 'data_type': 'String'}
    #list_filter.append(filter_dict)

    #filter_collection.insert(list_filter)  

    return jsonify({"filter_ranges":json_Data})
      



@app.route('/laptop_recommendations/remove_filter', methods=['POST'])
@required_params(required=['session','filter'])
def remove_filter():
    payload = request.get_json(force=True)
    filter_to_be_removed = {'filter': payload['filter']}
    if 'session' in payload and payload['session'] in sessions:
        session = sessions[payload['session']]
        if 'filters' not in session:
            return jsonify({'msg': 'no filters created'}), 404
        flag, indexval = search_and_get_index(session['filters'], filter_to_be_removed)
        if flag:
            median_dictionary = read_default_values()
            session['filters'].pop(indexval)
            filter_key  = filter_to_be_removed['filter']
            index_val, median_value = get_index_and_value(median_dictionary,filter_key)
            session['default'][index_val] = median_value
            # session.modified = True
            resp = cosine_in_elastic_search('laptop_recommendations', session['default'], 10)
            resp  = modify_response_laptop_data(resp,session['filters'])
            return jsonify({'laptop_data': resp,'msg':'{} removed'.format(filter_key),"session": payload['session']}), 200
        else:
            return jsonify({'msg': 'filter not applied yet..'}), 404

    return jsonify({"msg":"Invalid Session id "})




@app.route('/laptop_recommendations/edit_filter',methods= ['POST'])
@required_params(required=['data_type','session','filter'])
def edit_filter():
    payload = request.get_json(force=True)
    if 'data_type' not in payload or 'filter' not in payload or 'session' not in payload:
        return jsonify({'msg': 'Insufficient payload data'}), 400

    filter_name = payload['filter']
    db_minmax = Database(db_url=config['db_url'],db_name=database_name,collection_name=config['min_max_filter'])
    filter_minmax = db_minmax.find_all_values()
    
    if payload['session'] in sessions:
        session = sessions[payload['session']]
        if 'filters' not in session:
            return jsonify({'msg': 'filters not applied yet'}), 404    
        
        session_id = payload.pop('session')
        data_type = payload.pop('data_type')

        #to handle enumerate data
        if data_type == "Enum" and 'value' in payload:
            resp = cosine_in_elastic_search('laptop_recommendations', session['default'], 10,filter_name,payload['value'])
            filter_data = {'filter':filter_name,"value":payload['value']}
            flag, indexval = search_and_get_index(session['filters'], filter_data)
            
            if not flag :
                session['filters'].append(filter_data)
            else:
                session['filters'][indexval] = filter_data
            resp  = modify_response_laptop_data(resp,session['filters'])
            return jsonify({'laptop_data': resp,'filters': session['filters'],"session":session_id}), 200

        flag, indexval = search_and_get_index(session['filters'], payload)
        if flag:
            ## get the filter name and its index position from the config file
            median_dictionary = read_default_values()
            filter_index_value = list(median_dictionary.keys()).index(filter_name)

            flag1, edited_filter_index = search_and_get_index(filter_minmax, {'filter': filter_name} )
            if flag1:

                filter_min_value = filter_minmax[edited_filter_index]['min_value']
                filter_max_value = filter_minmax[edited_filter_index]['max_value']
            
                #update the filter value in front end
                new_filters = update_filter_values(indexval,session['filters'],payload)
                
                if new_filters:
                    # print("Default metrics: ",session['default'])
                    session['filters'] = new_filters

                    #update the filter value to be processed with cosine similarity in backend..
                    if 'value' in payload:

                        ## to handle boolean values.. 
                        if data_type == "Boolean":
                            if payload['value'] == False:
                                session['default'][filter_index_value] = 1 

                        elif data_type == "Number":
                            if 'operator' in payload:   
                                operator_value = payload['operator']
                                if operator_value == "<=":
                                    filter_updated_value = (payload['value']+filter_min_value)/2
                                elif operator_value == ">=":
                                    filter_updated_value = (payload['value']+filter_max_value)/2
                                elif operator_value == "==":
                                    filter_updated_value = payload['value']
                                else:
                                    filter_updated_value = payload['value']

                                db = Database(db_url=config['db_url'],db_name=database_name,collection_name=config['dataset_collection'])
                                session['default'][filter_index_value] = db.min_max_normalised_value(filter_name=filter_name,value=filter_updated_value)
                    
                            else:
                                filter_updated_value = payload['value']
                                db = Database(db_url=config['db_url'],db_name=database_name,collection_name=config['dataset_collection'])
                                session['default'][filter_index_value] = db.min_max_normalised_value(filter_name=filter_name,value=filter_updated_value)

                    resp = cosine_in_elastic_search('laptop_recommendations', session['default'], 10)
                    resp  = modify_response_laptop_data(resp,session['filters'])

                    return jsonify({'laptop_data': resp,'filters': session['filters'],"session":session_id}), 200

            return jsonify({'msg': 'Bad syntax'}), 400
        else:
            return jsonify({'msg': 'Filter not found or not appliet yet..'}), 404
    return jsonify({"msg":"Invalid Session id "})
    


##### admin code 
from preprocess_upload import *

ALLOWED_EXTENSIONS = set(['csv'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/upload',methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        new_filename = f'{filename.split(".")[0]}.csv'
        save_location = os.path.join('admin','uploaded_files', new_filename)
        file.save(save_location)
        columns_in_data = show_columns(save_location)[1]

        return jsonify({'msg':'Thanks for uploading','columns':columns_in_data})
    return jsonify({'msg':'Attach the csv file.'})



if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
