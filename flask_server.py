import imp
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'msg':'helloworld'}

if __name__ == '__main__':

    app.run(debug=True, port=5001)

