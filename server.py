from flask import Flask, request
from preprocess import cosine_in_elastic_search
app = Flask(__name__)


@app.route("/similar", methods=["POST"])
def get_recommendations():
    data = request.get_json(force=True)
    resp = cosine_in_elastic_search(data['index_name'], data['vector'],data['no_of_values'])
    return {'data': resp}


if __name__ == '__main__':

    app.run(debug=True, port=5001)
