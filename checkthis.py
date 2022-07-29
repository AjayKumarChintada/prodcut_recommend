from flask import Flask, session,jsonify
from flask_session import Session
from flask_cors import cross_origin
from product_recommendation import get_index_and_value, read_default_values

app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['SESSION_TYPE'] = 'filesystem'
#personal style preference compared to the first answer

Session(app)

@app.route('/set_val')
@cross_origin()
def set():
    session['key'] = [1,2,3]
    return 'ok'

@app.route('/get_val')
@cross_origin()
def get():
    return jsonify(session.get('key', 'not set'))

@app.route('/change_val')
@cross_origin()
def change():
    session['key'][1]= 'changed'
    session['key'].append('last added')
    return 'updated'







# if __name__ == '__main__':
# #     app.run(debug=True, port=5002, host='0.0.0.0')

# from utilities import * 
# data = [
#     {

#         "max_value": 3.6,

#         "min_value": 0.553,

#         "filter": "weight",

#         "data_type": "Number"

#     },
#     {

#         "max_value": 16.0,

#         "min_value": 1.0,

#         "filter": "ram",

#         "data_type": "Number"

#     },
#     {
#         "max_value": 194999.0,
#         "min_value": 14490.0,
#         "filter": "price",
#         "data_type": "Number"
#     }
# ]

# # data = read_default_values()

# data =  search_and_get_index(data,{'filter':'price'})
# print(data)
