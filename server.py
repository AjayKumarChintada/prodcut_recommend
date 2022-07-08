from crypt import methods
import json
import flask
from flask import Flask, request, session, jsonify
from product_recommendation import cosine_in_elastic_search, update_vector, get_default_vector
from flask_cors import CORS, cross_origin


app = Flask(__name__)


app.secret_key = 'LetsDoIt'


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
        return jsonify({'question_data': {"question": question_dictionary[0]['question'], 'options': question_dictionary[0]['options']}})

    else:
        data = request.get_json(force=True)
        question_number = data['question_number']
        choice_number = data['choice_number']

        question_filters = {
            0: {
                # indexes:  weight battery display
                #option number: [[index,replacements]


                0: [[0, 5, 6], [1, 1.75, 1.75]],
                1: [[0, 5, 6], [1.75, 1.2, 2]],
                2: [[0, 5, 6], [1.5, 1.5, 1.5]],
                'original_vals': {
                    0: {
                        'weight': 1.07,
                        'battery': 11.5,
                        'screen_size': 16.24
                    },
                    1: {
                        'weight': 2.51,
                        'battery': 6.0,
                        'screen_size': 17.8
                    },
                    2: {
                        'weight': 2.05,
                        'battery': 10,
                        'screen_size': 14.5
                    }
                }
            },
            ## RAM, Graphic ram, processor speed
            1: {

                0: [[1, 3, -2], [2, 1.75, 2]],
                1: [[1, 3, -2], [1, 1, 1]],
                2: [[1, 3, -2], [1.5, 1.4, 1.5]],
                'original_vals': {
                    0: {
                        'ram': 16,
                        'graphics': 12,
                        'processor': 4.7
                    },
                    1: {
                        'ram': 4.0,
                        'graphics': 0,
                        'processor': 1.1
                    },
                    2: {
                        'ram': 10,
                        'graphics': 8,
                        'processor': 2.90
                    }
                }

            },
            ## price
            2: {
                0: [[2], [1]],
                1: [[2], [1.5]],
                2: [[2], [2]],
                'original_vals': {
                    0: {
                        'price': 19990

                    },
                    1: {
                        'price': 68490
                    },
                    2: {
                        'price': 116990
                    }
                }

            },
            ## disk size, max memory support
            3: {
                0: [[4, 8], [2, 2]],
                1: [[4, 8], [1, 1]],
                2: [[4, 8], [1.5, 1.5]],

                'original_vals': {
                    0: {
                        'disk': 1024,
                        'memory': 32
                    },
                    1: {
                        'disk': 64,
                        'memory': 4
                    },
                    2: {
                        'disk': 512,
                        'memory': 18
                    }
                }
            }
        }

        if question_number not in question_filters:
            return jsonify({"Error": "invalid question number..."}), 404

        if question_number in question_filters:
            if choice_number not in question_filters[question_number]:
                return jsonify("Invalid Choice chosen..."), 404

        indexes, values = question_filters[question_number][choice_number]

        #for first time user initializing default vector first
        if 'default' not in session:
            vector = get_default_vector()
            session['default'] = vector

        # updating that default vector using payload
        session['default'] = update_vector(session['default'], indexes, values)
        resp = cosine_in_elastic_search(
            'laptop_recommendations', session['default'], 10)
        if question_number == len(question_dictionary)-1:
            return jsonify({
            'laptop_data': resp, 
            "question": "All questions done", "options": [],
            'filters': question_filters[question_number]['original_vals'][choice_number]}), 200

        if question_number in question_dictionary:

            #index name defined

            return jsonify({'laptop_data': resp,
                            "question_data": {"question": question_dictionary[question_number+1]['question'], 'options': question_dictionary[question_number+1]['options']},
                            'filters': question_filters[question_number]['original_vals'][choice_number]
                            }), 200


@app.route('/laptop_recommendations/get_labels', methods=['POST'])
@cross_origin()
def get_labels():
    data = request.get_json(force=True)
    num = data['question_number']
    questions_tags = {
        0: {

        }["weight", 'battery', 'screen_size'],
        1: ['ram', 'graphics', 'processor'],
        2: ['price'],
        3: ['storage', 'max_memory']}

    if num in questions_tags:
        return jsonify({"labels":  questions_tags[num]}), 200
    return jsonify({"error": "Question number not found.."}), 404


if __name__ == '__main__':

    app.run(debug=True, port=5001, host='0.0.0.0')
