from flask import Flask, render_template, request, redirect
from flask_restful import Resource, Api
from core.log_manager import LogManager
from flask.json import jsonify
from flask import Markup

app = Flask(__name__, static_url_path='/static')
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


api.add_resource(Search, '/api/Search/<search_string>')
api.add_resource(Reputation, '/api/Reputation/<hash>')

session = {'search_result': ''}

@app.route("/")
def index():
    global MANAGER
    search_result = session['search_result']
    search_data = ''
    if search_result is not None:
        for line in search_result:
            search_data += line
    search_data = Markup(search_data)

    error_data = ""
    for error in MANAGER.get_errors(html=True):
        error_data += error
    warn_data = ""
    for warning in MANAGER.get_warnings(html=True):
        warn_data += warning

    error_markup = Markup(error_data)
    warn_markup = Markup(warn_data)


    return render_template(
        'index.html',
        search_data=search_data,
        last_read_time=MANAGER.last_read_time,
        error_count=len(MANAGER.warn_error_index.index['error']),
        warn_count=len(MANAGER.warn_error_index.index['warn']),
        error_data=error_markup,
        warn_data=warn_markup
    )

@app.route('/Search', methods = ['POST', 'GET'])
def Search():
    global MANAGER
    html = True
    search_string = request.args.get('search_string')

    if not search_string:
        search_string = request.form['search_string']
    data = ''
    if search_string:
        data = MANAGER.search_index(search_string, html=html)
        if data is None:
            data = MANAGER.search_log_file(search_string, html=html)
    session['search_result'] = data

    return redirect('/')

if __name__ == '__main__':
    app.run()