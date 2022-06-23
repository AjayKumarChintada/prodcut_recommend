from crypt import methods
from flask import Flask, request
from product_recommendation import cosine_in_elastic_search





app = Flask(__name__)


@app.route("/similar", methods=["POST"])
def get_recommendations():
    data = request.get_json(force=True)
    if 'no_of_values' in data and data['no_of_values']:
        resp = cosine_in_elastic_search(
            data['index_name'], data['vector'], data['no_of_values'])
    else:
        resp = cosine_in_elastic_search(
            data['index_name'], data['vector'], 10)

    return {'data': resp}


@app.route("/questions/<int:question_number>", methods=["GET"])
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
        return "invalid question number...!"


if __name__ == '__main__':

    app.run(debug=True, port=5001)
