from crypt import methods
from flask import Flask, request
from product_recommendation import cosine_in_elastic_search,update_vector,get_default_vector



app = Flask(__name__)


@app.route("/laptop_recommendations/similar", methods=["POST"])
def get_recommendations():
    data = request.get_json(force=True)
    if 'no_of_values' in data and data['no_of_values']:
        resp = cosine_in_elastic_search(
            data['index_name'], data['vector'], data['no_of_values'])
    else:
        resp = cosine_in_elastic_search(
            data['index_name'], data['vector'], 10)

    return {'data': resp}


@app.route("/laptop_recommendations/questions/<int:question_number>", methods=["GET"])
def get_questions(question_number):
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
    if question_number in question_dictionary:
        return question_dictionary[question_number]
    else:
        return "invalid question number...!",404


@app.route("/laptop_recommendations/user_choices/", methods=["POST"])
def user_choices():

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
        return "invalid question number...", 404
    if question_number in question_filters :
        if choice_number not in question_filters[question_number]:
            return "Invalid Choice chosen...", 404
    # indexes,values = question_filters[question_number][choice_number]
    # return {'vector':vec}
    return {'updations': question_filters[question_number][choice_number]},200






if __name__ == '__main__':

    app.run(debug=True, port=5001)
