from flask import Flask, render_template, request, redirect
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

session = {'search_result': ''}

@app.route("/")
def index():
    search_result = session['search_result']
    search_data = ''
    if search_result is not None:
        for line in search_result:
            search_data += line
    return render_template('index.html', search_data=search_data)

@app.route('/Search', methods = ['POST'])
def Search():
    global MANAGER
    search_string = request.form['search_string']
    data = MANAGER.search_index(search_string)
    if data is None:
        data = MANAGER.search_log_file(search_string)
    session['search_result'] = data
    return redirect('/')

if __name__ == '__main__':
    app.run()