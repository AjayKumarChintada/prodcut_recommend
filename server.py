import json
import flask
from flask import Flask, request, session, jsonify
from product_recommendation import cosine_in_elastic_search, update_vector,read_default_values,get_index_and_value
from flask_cors import CORS, cross_origin
from database_utilities import Database




app = Flask(__name__)
app.secret_key = 'alpha'
CORS(app, supports_credentials=True)
config = read_default_values('config.json')
database_url = config['db_url']
database_name = config['db_name']

 
@app.route('/laptop_recommendations/del')
@cross_origin()
def clear_session():
    session.clear()
    return jsonify({'msg': 'session cleared..'})


@app.route("/laptop_recommendations/similar", methods=["POST"])
@cross_origin()
def get_recommendations():
    """takes a vector and gives the similar items 10 by default

    Returns:
        object: similar matches using cosine similarity
    """
    data = request.get_json(force=True)
    if 'no_of_values' in data and data['no_of_values']:
        resp = cosine_in_elastic_search(
            data['index_name'], data['vector'], data['no_of_values'])
    else:
        resp = cosine_in_elastic_search(
            data['index_name'], data['vector'], 10)
    return {'data': resp}


def make_filter_object(array: list):
    """ returns list of dictionaries or filter objects
    Args:
        array (list): list of list
    """
    data = []
    for resp in array:
        metrics = {
            'filter': resp[0],
            'value': resp[1],
            "operator": resp[3],
            "metric": resp[2]
        }
        data.append(metrics)
    return data


def search_and_get_index(filters, filter):
    """search for same filter and returns 1 and its index value if found else 0

    Args:
        obj (filters oject list): list of filter objects
        b (single object): a single filter object to search

    Returns:
        (1,index_val)/ 0: tuple of index value and flag or 0
    """
    for indexval in range(len(filters)):
        if filter['filter'] == filters[indexval]['filter']:
            return 1, indexval
    return 0, None


@app.route("/laptop_recommendations/user_choices", methods=["POST", "GET"])
@cross_origin()
def user_choices():
    """takes question number and choice number 

    Returns:
        json object: array of user vector already updated
    """
   
    collection_name = config['collection_name']


    db = Database(db_url=database_url,db_name=database_name,collection_name=collection_name)

    if flask.request.method == 'GET':
        resp = db.get_question_with_id(0)
        resp['next_question_number'] = 1
        return jsonify({'question_data':resp})

    else:
        data = request.get_json(force=True)
        question_number = data['question_number']
        choice_number = data['choice_number']

        
        questions_data = db.get_question_with_id(question_number+1)
        if not questions_data and question_number != db.get_last_record_id():
            return jsonify({"Error": "invalid question number..."}), 404

        ## database connection for options collection
        options_collection_db = Database(database_url,database_name,config['options_collection'])
        results = options_collection_db.get_question_with_id(id_val=question_number) 
        if not results:
                return jsonify("Invalid Choice chosen..."), 404

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

        # condition to handle last question
        if question_number == db.get_last_record_id():
            return jsonify({
                'laptop_data': resp,
                'question_data': {"question": 'All questions done', 'options': [], 'next_question_number': -1},
                'filters': session['filters'],
            }), 200

        # questions
        if questions_data:
            questions_data['next_question_number'] = question_number+1
            return jsonify({'laptop_data': resp,
                            "question_data": questions_data,
                            'filters': session['filters']
                            }), 200

@app.route('/laptop_recommendations/remove_filter', methods=['POST'])
@cross_origin()
def remove_filter():
    payload = request.get_json(force=True)
    filter_to_be_removed = {'filter': payload['filter']}
    if 'filters' not in session:
        return jsonify({'msg': 'no filters created'}), 404
    flag, indexval = search_and_get_index(session['filters'], filter_to_be_removed)
    if flag:
        median_dictionary = read_default_values()
        session['filters'].pop(indexval)
        filter_key  = filter_to_be_removed['filter']
        index_val, median_value = get_index_and_value(median_dictionary,filter_key)
        session['default'][index_val] = median_value
        session.modified = True
        resp = cosine_in_elastic_search('laptop_recommendations', session['default'], 10)
        return jsonify({'laptop_data:': resp,'msg':'{} removed'.format(filter_key)}), 200
    else:
        return jsonify({'msg': 'filter not applied yet..'}), 404
    



def update_filter_values(index,filters,new_filter):
    filter_to_be_updated = filters[index]
    for key in new_filter:
        if key in filter_to_be_updated:
            filter_to_be_updated[key] = new_filter[key]
        else:
            return 0
    filters[index] = filter_to_be_updated
    return filters

@app.route('/laptop_recommendations/edit_filter',methods= ['POST'])
@cross_origin()
def edit_filter():
    payload = request.get_json(force=True)
    if 'filters' not in session:
        return jsonify({'msg': 'filters not applied yet'}), 404    

    flag, indexval = search_and_get_index(session['filters'], payload)
    if flag:
        ## get the filter name and its index position from the config file
        filter_name = payload['filter']
        median_dictionary = read_default_values()
        filter_index_value = list(median_dictionary.keys()).index(filter_name)

        #update the filter value in front end
        new_filters = update_filter_values(indexval,session['filters'],payload)
        if new_filters:
            print("Default metrics: ",session['default'])
            session['filters'] = new_filters

            #update the filter value to be processed with cosine similarity in backend..
            if 'value' in payload:
                ## to handle boolean values.. 
                if payload['value'] == False:
                    session['default'][filter_index_value] = 1 
                else:
                    filter_updated_value = payload['value']
                    db = Database(db_url=config['db_url'],db_name=database_name,collection_name=config['dataset_collection'])
                    session['default'][filter_index_value] = db.min_max_normalised_value(filter_name=filter_name,value=filter_updated_value)
            session.modified = True
            resp = cosine_in_elastic_search('laptop_recommendations', session['default'], 10)

            print("updated metrics: ",session['default'])
            return jsonify({'laptop_data': resp,'filters': session['filters']}), 200

        return jsonify({'msg': 'Bad syntax'}), 400
    else:
        return jsonify({'msg': 'Filter not found or not appliet yet..'}), 404



@app.route('/laptop_recommendations/current_vector')
@cross_origin()
def get_current_vector():
    return jsonify({'msg': session['default']}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
