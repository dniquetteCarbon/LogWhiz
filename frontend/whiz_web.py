from flask import Flask, render_template, request, redirect
from flask_restful import Resource, Api
from core.log_manager import LogManager
from flask.json import jsonify
from flask import Markup
from core.db_manager import LOG_DB, DBManager
from core.jenkins_helper import JenkinsHelper
from core.config import Config
import re
import argparse

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
LOG_DB.init_app(app)
LOG_DB.create_all(app=app)
db_manager = DBManager(LOG_DB)
api =Api(app)

j_helper = JenkinsHelper()

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

session = {'search_result': None,
           'title': 'Overview'}


@app.route("/")
def index():

    if db_manager.database_empty:
        update_logs()
    elif session['search_result'] is None:
        session['search_result'] = db_manager.query_total_errors()

    return render_template(
        'index.html',
        title=session['title']
    )


@app.route('/home', methods = ['POST', 'GET'])
def home():
    session['search_result'] = db_manager.query_total_errors()
    session['title'] = 'Overview'
    return redirect('/')

@app.route('/topten', methods = ['POST', 'GET'])
def top_ten():
    session['search_result'] = db_manager.query_top_ten()
    session['title'] = 'Top Ten'
    return redirect('/')

@app.route('/loadlogs', methods = ['POST', 'GET'])
def load_logs():
    return jsonify(session['search_result'])


@app.route('/updatelogs', methods = ['POST', 'GET'])
def update_logs():
    global MANAGER

    latest_build = j_helper.get_latest_build_num()
    stored_builds = db_manager.query_jenkins_job_builds()

    if latest_build not in stored_builds:
        dl_result = j_helper.download_confer_log()
        job_id = db_manager.add_jenkins_job(dl_result['job_name'], dl_result['build_num'], dl_result['build_time'])
        db_manager.commit()
        for log_file in dl_result['confer_logs']:
            match = re.search(r'[0-9]+-(.*)-([0-9]+-[0-9]+-[0-9]+-[0-9]+)-', log_file)
            guest_os = match.group(1)
            sensor_version = match.group(2).replace('-', '.')
            MANAGER.set_log(log_file)
            data = MANAGER.search_log_file('ERROR')
            errors = MANAGER.reduce_similar_errors(data)
            for error, count in errors.items():
                line_id = db_manager.add_log_line(error, None)
                db_manager.add_job_line_error(line_id, job_id, count, guest_os, sensor_version)
                db_manager.commit()
        #data = db_manager.query_errors()

        session['search_result'] = db_manager.query_total_errors()
    data = session['search_result']
    db_manager.delete_old_entries()
    return jsonify(data)

@app.route("/logwhiz")
def logwhiz():
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
        'whiz_index.html',
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


@app.route('/SearchError', methods = ['POST', 'GET'])
def SearchError():
    global MANAGER
    search_string = request.args.get('search_string')

    if not search_string:
        search_string = request.form['search_string']

    data = db_manager.query_errors(search_string)
    session['search_result'] = data
    session['title'] = search_string

    return redirect('/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--user',
        help='Username of Jenkins User',
        required=True
    )
    parser.add_argument(
        '--apikey',
        help='API key for specified user',
        required=True
    )
    args = parser.parse_args()
    j_helper.login_jenkins(args.user, args.apikey)
    app.run()
