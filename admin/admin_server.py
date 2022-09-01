import flask
from flask import Flask, jsonify, request, session
from flask_cors import CORS
import functools


app = Flask(__name__)
CORS(app)


def validate_request(f):
  @functools.wraps(f)
  def decorator(*args, **kwargs):
    data = flask.request.get_json()
    if not data:
      return({'msg': "no json sent"})
    return f(*args, **kwargs)
  return decorator


def required_params(required):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            _json = request.get_json()
            ## to check missing keys of json object
            missing = [r for r in required if r not in _json]
            if missing:
                response = {
                    "status": "error",
                    "message": "Request JSON is missing some required param key",
                    "missing": missing
                }
                return jsonify(response), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/admin/api_check", methods=["POST",'GET'])
@required_params(required=['session'])
def get_recommendations():
    if flask.request.method == "GET":
        return {"msg":"get request"}
    data = request.get_json(force=True)
    return {"data":data}


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
