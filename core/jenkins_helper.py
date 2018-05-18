import os
import re
import tempfile
from jenkinsapi.utils.requester import Requester
from jenkinsapi.jenkins import Jenkins

JENKINS_URL = 'https://jenkins-qa.cbenglab.com'
JENKINS_JOB = 'cbda_end_to_end_windows'


class JenkinsHelper:

    def __init__(self, jenkins_url: str = None):
        self.jenkins_url = jenkins_url or JENKINS_URL
        self.download_dir = os.environ.get('DOWNLOAD_DIR') or self.get_tmp_dir()
        self.server = None

    def login_jenkins(self, username: str, password: str):
        req = Requester(
            username=username,
            password=password,
            baseurl=JENKINS_URL,
            ssl_verify=False)
        self.server = Jenkins(self.jenkins_url, requester=req)

    def get_tmp_dir(self):
        download_dir = None
        temp_dir = tempfile.gettempdir()
        for temp in os.listdir(temp_dir):
            match = re.search('(cbd_log_.*)', temp)
            if match:
                download_dir = os.path.join(temp_dir, match.group(1))

        if download_dir is None:
            download_dir = tempfile.mkdtemp(prefix='cbd_log_')
        return download_dir

    def download_job(self, job_name: str, build_number: int = None):
        return {
            'confer_log': self.download_confer_log(job_name, build_number),
            'results': self.download_results(job_name, build_number)
        }

    def get_latest_build_num(self, job_name: str = None):
        job_name = job_name or JENKINS_JOB
        job = self.server.get_job(job_name)
        last_build = job.get_last_build()
        return last_build.buildno

    def download_confer_log(self, job_name: str = None):
        job_name = job_name or JENKINS_JOB
        job = self.server.get_job(job_name)
        last_build = job.get_last_build()
        artifacts = last_build.get_artifact_dict()
        build_num = last_build.buildno
        build_time = last_build._data['timestamp']

        confer_logs = []
        for artifact_name in artifacts:
            if 'system_snapshot' in artifact_name and 'confer.log' in artifact_name:
                artifacts[artifact_name].save_to_dir(self.download_dir)
                confer_logs.append(os.path.join(self.download_dir, artifact_name))

        return {
            'job_name': job_name,
            'build_num': build_num,
            'build_time': build_time,
            'confer_logs': confer_logs
        }

    def download_results(self, job_name: str, build_number: int = None):
        pass
