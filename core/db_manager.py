from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.exc import IntegrityError
import operator

LOG_DB = SQLAlchemy()


class LogLine(LOG_DB.Model):
    """
    Tracks unique error messages
    """
    __tablename__ = 'logline'
    id = LOG_DB.Column(LOG_DB.Integer, primary_key=True)
    text = LOG_DB.Column(LOG_DB.String(64), unique=True)
    definition = LOG_DB.Column(LOG_DB.String(64), nullable=True)

    def __repr__(self):
        return '<logline {}>'.format(self.id)


class JenkinsJob(LOG_DB.Model):
    """
    Tracks basic job info
    """
    __tablename__ = 'jenkinsjob'
    id = LOG_DB.Column(LOG_DB.Integer, primary_key=True)
    name = LOG_DB.Column(LOG_DB.String(64))
    build_num = LOG_DB.Column(LOG_DB.Integer, unique=True)
    date = LOG_DB.Column(LOG_DB.Integer, unique=False)

    def __repr__(self):
        return '<jenkinsjob {}>'.format(self.job_num)


class JobLineError(LOG_DB.Model):
    """
    Counts Errors Per Job
    """
    __tablename__ = 'joblineerror'
    id = LOG_DB.Column(LOG_DB.Integer, primary_key=True)
    log_id = LOG_DB.Column(LOG_DB.Integer, LOG_DB.ForeignKey('logline.id'))
    job_id = LOG_DB.Column(LOG_DB.Integer, LOG_DB.ForeignKey('jenkinsjob.id'))
    error_count = LOG_DB.Column(LOG_DB.Integer, unique=False)
    guest_os = LOG_DB.Column(LOG_DB.String(64))
    sensor_version = LOG_DB.Column(LOG_DB.String(64))

    log_line = LOG_DB.relationship('LogLine', foreign_keys=[log_id])
    job_info = LOG_DB.relationship('JenkinsJob', foreign_keys=[job_id])

    def __repr__(self):
        return '<joblineerror JOB: {} - LINE: {}>'.format(self.job_id, self.log_id)

class DBManager:
    def __init__(self, db: Flask):
        self.db = db

    @property
    def database_empty(self):
        result = JobLineError.query.all()
        if result:
             return False
        return True

    def add_log_line(self, text: str, definition: str):
        log_line = LogLine(
            text=text,
            definition=definition
        )
        try:
            id = self.add_to_db(log_line)
            return id
        except IntegrityError:
            self.db.session.rollback()
            lines = LogLine.query.all()
            for line in lines:
                if text == line.text:
                    return line.id

    def add_jenkins_job(self, job_name: str, build_num: int, date: float):
        jenkins_job = JenkinsJob(
            name=job_name,
            build_num=build_num,
            date=date
        )
        try:
            id = self.add_to_db(jenkins_job)
            return id
        except IntegrityError:
            self.db.session.rollback()
            jobs = JenkinsJob.query.all()
            for job in jobs:
                if build_num == job.build_num:
                    return job.id

    def add_job_line_error(self, log_id: int, job_id: int, error_count: int, guest_os: str, sensor_version: str):
        job_line_error = JobLineError(
            log_id=log_id,
            job_id=job_id,
            error_count=error_count,
            guest_os = guest_os,
            sensor_version = sensor_version
        )
        return self.add_to_db(job_line_error)

    def add_to_db(self, obj_to_add):
        self.db.session.add(obj_to_add)
        self.db.session.flush()
        return obj_to_add.id

    def commit(self):
        try:
            self.db.session.commit()
        # If we try to commit non unique lines
        except IntegrityError:
            pass

    def query_jobs(self):
        data = JenkinsJob.query.all()

        job_data = []
        for job in data:
            job_data.append({
                'name': job.name,
                'build_num': job.build_num
            })

        return job_data

    def query_errors(self, query_string: str):
        '''
        error.error_count
        error.job_info.name
        error.job_info.build_num
        error.job_info.date
        error.log_line.text
        error.log_line.definition

        :return:
        '''
        data = JobLineError.query.all()

        error_data = {}

        # initialize dict for matches
        for error in data:
            if query_string in error.log_line.text:
                error_data[error.log_line.text] = {}
            elif query_string in error.guest_os:
                error_data[error.guest_os] = {}
                error_data[error.log_line.text] = {}
            elif query_string in error.sensor_version:
                error_data[error.sensor_version] = {}
                error_data[error.log_line.text] = {}

        # initialize for dates
        for error in data:
            if query_string in error.guest_os:
                error_data[error.guest_os][error.job_info.date] = 0
                error_data[error.log_line.text][error.job_info.date] = 0
            elif query_string in error.sensor_version:
                error_data[error.sensor_version][error.job_info.date] = 0
                error_data[error.log_line.text][error.job_info.date] = 0
            elif query_string in error.log_line.text:
                error_data[error.log_line.text][error.job_info.date] = 0

        # count errors
        for error in data:
            if query_string in error.log_line.text:
                error_data[error.log_line.text][error.job_info.date] += error.error_count
            elif query_string in error.guest_os:
                error_data[error.guest_os][error.job_info.date] += error.error_count
                error_data[error.log_line.text][error.job_info.date] += error.error_count
            elif query_string in error.sensor_version:
                error_data[error.sensor_version][error.job_info.date] += error.error_count
                error_data[error.log_line.text][error.job_info.date] += error.error_count

        return self.format_for_chart(error_data)

    def query_total_errors(self):

        data = JobLineError.query.all()
        error_data = {'total': {}}
        for error in data:
            error_data[error.guest_os] = {}

        for error in data:
            error_data['total'][error.job_info.date] = 0
            error_data[error.guest_os][error.job_info.date] = 0
        for error in data:
            error_data['total'][error.job_info.date] += error.error_count
            error_data[error.guest_os][error.job_info.date] += error.error_count

        return self.format_for_chart(error_data)

    def query_top_ten(self):
        data = JobLineError.query.all()

        error_data = {}
        for error in data:
            error_data[error.log_line.text] = 0
        for error in data:
            error_data[error.log_line.text] += error.error_count


        if len(error_data.items()) >= 10:
            top_ten = dict(sorted(error_data.items(), key=operator.itemgetter(1), reverse=True)[:10])
        else:
            top_ten = error_data

        sensor_version = {}
        final_error_data = {}
        for error in data:
            if error.log_line.text in top_ten.keys():
                final_error_data[error.log_line.text] = {}
        for error in data:
            if error.log_line.text in top_ten.keys():
                final_error_data[error.log_line.text][error.job_info.date] = 0
                sensor_version[error.log_line.text] = error.sensor_version
        for error in data:
            if error.log_line.text in top_ten.keys():
                final_error_data[error.log_line.text][error.job_info.date] += error.error_count

        return self.format_for_chart(final_error_data, sensor_version)

    def format_for_chart(self, data_dict: {}, sensor_version: {} = None):
        graph_temp = {}
        pie_temp = {}
        last_date = 0
        for type, data in data_dict.items():
            for date, total in data.items():
                if date > last_date:
                    last_date = date

        for type, data in data_dict.items():
            graph_temp[type] = []
            pie_temp[type] = 0
            dates = data.keys()
            dates = list(dates)
            dates.sort()
            for date in dates:
                t_data = {'x': date, 'y': data[date]}
                if date == last_date:
                    pie_temp[type] += data[date]
                if sensor_version:
                    t_data['label'] = sensor_version[type]
                graph_temp[type].append(t_data)
            '''
            for date, total in data.items():
                data = {'x': date, 'y': total}
                if date == last_date:
                    pie_temp[type] += total
                if sensor_version:
                    data['label'] = sensor_version[type]
                graph_temp[type].append(data)
            '''

        pie_final = []
        for name, y in pie_temp.items():
            pie_final.append({
                'name': name,
                "y": y,
                "drilldown": name
            })

        return {
            'line_data': graph_temp,
            'pie_data': pie_final
        }



    def query_jenkins_job_builds(self):
        data = JenkinsJob.query.all()
        build_nums = []

        for build in data:
            build_nums. append(build.build_num)

        return build_nums

