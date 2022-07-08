
from flask import Flask
from numpy import number

# app = Flask(__name__)

# @app.route('/')
# def hello():
#     return {'msg':'helloworld'}

# if __name__ == '__main__':

#     app.run(debug=True, port=5005)


questions_tags = {
    0: ["weight", 'battery', 'screen_size'],
    1: ['ram', 'graphics', 'processor'],
    2: ['price'],
    3: ['storage', 'max_memory']
}

def get_labels(num):
    return questions_tags[num]


print(get_labels(1))