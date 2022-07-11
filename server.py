from crypt import methods
import json
import flask
from flask import Flask, request, session, jsonify
from product_recommendation import cosine_in_elastic_search, update_vector, get_default_vector
from flask_cors import CORS, cross_origin


app = Flask(__name__)


app.secret_key = 'aafdj'


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


def make_filter_object(array:list):
    """ returns list of dictionaries or filter objects
    Args:
        array (list): list of list
    """
    data = []
    for resp in array: 
        metrics = {
            'filter': resp[0],
            'value': resp[1],
            "operator":resp[3],
            "metric": resp[2]
            
        }

        data.append(metrics)
    return data

def search_and_get_index(obj,b):
    """search for same filter and returns 1 and its index value if found else 0

    Args:
        obj (filters oject list): list of filter objects
        b (single object): a single filter object to search

    Returns:
        (1,index_val)/ 0: tuple of index value and flag or 0
    """
    for indexval in range(len(obj)):
        if b['filter'] == obj[indexval]['filter']:
            return 1,indexval
    return 0

@app.route("/laptop_recommendations/user_choices", methods=["POST", "GET"])
@cross_origin()
def user_choices():
    """takes question number and choice number 

    Returns:
        json object: array of user vector already updated
    """

    question_dictionary = {
        0: {
            'question': "How often you travell along with your laptop?",
            'options': ["yes, I travell a lot.", "Not much, Usaully stay at my desk.", "Do not have any specification .", ]
        },

        1: {
            "question":  "What is your laptop typically used for ?",
            'options': ['gaming and media development', 'office and general business purpose', 'student usage/design and development']

        },

        2: {

            "question": "What is the price range you want for your laptop ?",
            'options': ["less than 30000 / low range", "30000 to 50000 / mid range", "more than 50000 / high range"]

        },
        3: {
            "question": "Do you store a lot of content in your device?",
            'options': ['Yes, a lot. Need large storages', 'No I dont. Use it only for official purposes', ' Moderate usage, nothing specific. Anything works']

        }

    }

    if flask.request.method == 'GET':
        return jsonify({'question_data': {"question": question_dictionary[0]['question'], 'options': question_dictionary[0]['options'], 'next_question_number': 1}})

    else:
        data = request.get_json(force=True)
        question_number = data['question_number']
        choice_number = data['choice_number']

        question_filters = {
            0: {
                # indexes:  weight battery display
                # option number: [[index,replacements]


                0: [[0, 5, 6], [1, 1.75, 1.75]],
                1: [[0, 5, 6], [1.75, 1.2, 2]],
                2: [[0, 5, 6], [1.5, 1.5, 1.5]],
                'original_vals': {
                    0: [
                        ['weight', 1.07,'Kg','~'],
                        ['battery', 11.5,'Hours','~'],
                        ['screen_size', 16.24,'Inches','~']
                    ],
                    1: [
                        ['weight', 2.51,'Kg','~'],
                        ['battery', 6.0,'Hours','~'],
                        ['screen_size', 17.8,'Inches','~']
                    ],
                    2: [
                        ['weight', 2.05,'Kg','~'],
                        ['battery', 10,'Hours','~'],
                        ['screen_size', 14.5,'Inches','~']
                    ]
                }
            },
            # RAM, Graphic ram, processor speed
            1: {

                0: [[1, 3, -2], [2, 1.75, 2]],
                1: [[1, 3, -2], [1, 1, 1]],
                2: [[1, 3, -2], [1.5, 1.4, 1.5]],
                'original_vals': {
                    0: [
                        ['ram', 16,'GB','~'],
                        ['graphics', True,'GPU','='],
                        ['processor', 4.7,'GHz','~']
                    ],
                    1: [
                        ['ram', 4.0,'GB','~'],
                        ['graphics',  False,'GPU','='],
                        ['processor', 1.1,'GHz','~']
                    ],
                    2: [
                        ['ram', 10,'GB','~'],
                        ['graphics',  True,'GPU','='],
                        ['processor', 2.90,'GHz','~']
                    ]
                }

            },
            # price
            2: {
                0: [[2], [1]],
                1: [[2], [1.5]],
                2: [[2], [2]],
                'original_vals': {
                    0: [
                        ['price', 19990,'INR','~']
                    ],
                    1: [
                        ['price', 68490,'INR','~']
                    ],
                    2: [
                        ['price', 116990,'INR','~']
                    ]
                }

            },
            # disk size, max memory support
            3: {
                0: [[4, 8], [2, 2]],
                1: [[4, 8], [1, 1]],
                2: [[4, 8], [1.5, 1.5]],

                'original_vals': {
                    0: [
                        ['disk', 1024,'GB','~'],
                        ['memory',  32,'GB','~']

                    ],
                    1: [
                        ['disk', 64,'GB','~'],
                        ['memory',  4,'GB','~']
                    ],
                    2: [
                        ['disk', 512,'GB','~'],
                        ['memory',  18,'GB','~']
                    ]
                }
            }
        }

        if question_number not in question_filters:
            return jsonify({"Error": "invalid question number..."}), 404

        if question_number in question_filters:
            if choice_number not in question_filters[question_number]:
                return jsonify("Invalid Choice chosen..."), 404

        indexes, values = question_filters[question_number][choice_number]
        filters = question_filters[question_number]['original_vals'][choice_number]
        

        # for first time user initializing default vector first
        if 'default' not in session:
            vector = get_default_vector()
            session['default'] = vector


        ## logic to append filters to backend 
        filter_objects = make_filter_object(filters)
        if 'filters' not in session:
            session['filters'] = filter_objects

        else:
            for filter_object in filter_objects:
                if not search_and_get_index(session['filters'],filter_object):
                    session['filters'].append(filter_object)

            


        # updating that default vector using payload
        session['default'] = update_vector(session['default'], indexes, values)

        # updating filters
        resp = cosine_in_elastic_search(
            'laptop_recommendations', session['default'], 10)

        # condition to handle last question
        if question_number == len(question_dictionary)-1:
            return jsonify({
                'laptop_data': resp,
                'question_data': {"question": 'All questions done', 'options': [], 'next_question_number': -1},
                'filters': session['filters'],

            }), 200

        # questions
        if question_number in question_dictionary:
            return jsonify({'laptop_data': resp,
                            "question_data": {"question": question_dictionary[question_number+1]['question'], 'options': question_dictionary[question_number+1]['options'], 'next_question_number': question_number+1},
                            'filters': session['filters']
                            }), 200


@app.route('/laptop_recommendations/remove_filter',methods=['POST'])
@cross_origin()
def remove_filter():
    payload = request.get_json(force=True)
    filter_to_be_removed = {'filter': payload['filter']}
    _, indexval = search_and_get_index(session['filters'],filter_to_be_removed)
    del session['filters'][indexval]
    
    return jsonify( session['filters']),200




if __name__ == '__main__':

    app.run(debug=True, port=5001, host='0.0.0.0')
