import flask
from flask import Flask, request, session
from product_recommendation import cosine_in_elastic_search, update_vector, get_default_vector
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
app.secret_key = 'LetsDoIt'


# @app.route("/laptop_recommendations/similar", methods=["POST"])
# def get_recommendations():
#     """takes a vector and gives the similar items 10 by default

#     Returns:
#         object: similar matches using cosine similarity
#     """
#     data = request.get_json(force=True)
#     if 'no_of_values' in data and data['no_of_values']:
#         resp = cosine_in_elastic_search(
#             data['index_name'], data['vector'], data['no_of_values'])
#     else:
#         resp = cosine_in_elastic_search(
#             data['index_name'], data['vector'], 10)

#     return {'data': resp}


# @app.route("/laptop_recommendations/question/<int:question_number>", methods=["GET"])
# def get_question(question_number):
#     """takes question number and returns question and options json object

#     Args:
#         question_number (int): takes question number

#     Returns:
#         dictionary: questions and options if not valid number returns error
#     """
#     question_dictionary = {
#         0: {
#             'question': "How often you travell along with your laptop?",
#             'options': ["yes, I travell a lot.", "Not much, Usaully stay at my desk.", "Do not have any specification .", ]
#         },

#         1: {
#             "question":  "What is your laptop typically used for ?",
#             'options': ['gaming and media development', 'office and general business purpose', 'student usage/design and development']

#         },

#         2: {

#             "question": "What is the price range you want for your laptop ?",
#             'options': ["less than 30000 / low range", "30000 to 50000 / mid range", "more than 50000 / high range"]

#         },
#         3: {
#             "question": "Do you store a lot of content in your device?",
#             'options': ['Yes, a lot. Need large storages', 'No I dont. Use it only for official purposes', ' Moderate usage, nothing specific. Anything works']


#         }

#     }
#     if question_number in question_dictionary:
#         return question_dictionary[question_number]
#     else:
#         return "invalid question number...!", 404


# @app.route("/laptop_recommendations/questions", methods=["GET"])
# def get_questions():
#     """gives all questions in databse

#     Returns:
#         _type_: _description_
#     """
#     question_dictionary = {
#         0: {
#             'question': "How often you travell along with your laptop?",
#             'options': ["yes, I travell a lot.", "Not much, Usaully stay at my desk.", "Do not have any specification .", ]
#         },

#         1: {
#             "question":  "What is your laptop typically used for ?",
#             'options': ['gaming and media development', 'office and general business purpose', 'student usage/design and development']

#         },

#         2: {

#             "question": "What is the price range you want for your laptop ?",
#             'options': ["less than 30000 / low range", "30000 to 50000 / mid range", "more than 50000 / high range"]

#         },
#         3: {
#             "question": "Do you store a lot of content in your device?",
#             'options': ['Yes, a lot. Need large storages', 'No I dont. Use it only for official purposes', ' Moderate usage, nothing specific. Anything works']

#         }

#     }
#     return {'questions': question_dictionary}


@app.route("/laptop_recommendations/user_choices", methods=["POST", "GET"])
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
        return {"question": question_dictionary[0]['question'], 'options': question_dictionary[0]['options']}

    else:
        data = request.get_json(force=True)
        question_number = data['question_number']
        choice_number = data['choice_number']

        question_filters = {
            0: {
                # indexes:  weight battery screensize
                #option number: [[index,replacements]

                0: [[0, 5, 6], [1, 1.75, 1.75]],
                1: [[0, 5, 6], [1.75, 1.2, 2]],
                2: [[0, 5, 6], []]
            },
            ## RAM, Graphic ram, processor speed
            1: {

                0: [[1, 3, -2], [2, 1.75, 2]],
                1: [[1, 3, -2], [1, 1, 1]],
                2: [[1, 3, -2], [1.5, 1.4, 1.5]]


            },
            ## price
            2: {
                0: [[2], [1]],
                1: [[2], [1.5]],
                2: [[2], [2]]

            },
            ## disk size, max memory support
            3: {
                0: [[4, 8], [2, 2]],
                1: [[4, 8], [1, 1]],
                2: [[4, 8], [1.5, 1.5]]
            }
        }

        if question_number not in question_filters:
            return {"Error": "invalid question number..."}, 404

        if question_number in question_filters:
            if choice_number not in question_filters[question_number]:
                return "Invalid Choice chosen...", 404

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
            return {'laptop_data': resp, "question": "All questions done", "options": []}, 200

        if question_number in question_dictionary:

            #index name defined

            return {'laptop_data': resp, "question": question_dictionary[question_number+1]['question'], 'options': question_dictionary[question_number+1]['options']}, 200


if __name__ == '__main__':

    app.run(debug=True, port=5001)
