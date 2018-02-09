from flask import Flask, request
from flask_restful import Resource, Api
from core.log_manager import LogManager
from flask.json import jsonify

app = Flask(__name__)
api =Api(app)

MANAGER = LogManager()


class Search(Resource):
    def get(self, search_string):
        global MANAGER
        data = MANAGER.search_index(search_string)
        result = {'data': data}
        return jsonify(result)


class Reputation(Resource):
    def get(self, hash):
        global MANAGER
        data = MANAGER.get_repuation_def(hash)
        result = {'data': data}
        return jsonify(result)


api.add_resource(Search, '/Search/<search_string>')
api.add_resource(Reputation, '/Reputation/<hash>')

if __name__ == '__main__':
    app.run()