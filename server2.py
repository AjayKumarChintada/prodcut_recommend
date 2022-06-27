
import re
from flask import Flask, request, session

from product_recommendation import get_default_vector, update_vector

app = Flask(__name__)

app.secret_key = 'hihow'


@app.route('/', methods=['POST'])
def update_vector_api():
    data = request.get_json(force=True)
    question_number = data['question_number']
    choice_number = data['choice_number']
    # return {'del': session['default']}

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

    if question_number in question_filters:
        if choice_number not in question_filters[question_number]:
            return "Invalid Choice chosen...", 404

    indexes, values = question_filters[question_number][choice_number]

    if 'default' not in session:
        vector = get_default_vector()
        session['default'] = vector

    session['default'] = update_vector(session['default'], indexes, values)
    return {'else': session['default']}


if __name__ == '__main__':

    app.run(debug=True, port=5009)
