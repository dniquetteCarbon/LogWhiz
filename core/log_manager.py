import platform
import threading
import datetime
import os
import re
from core.log_parser import LogParser
from core.whiz_index import WhizIndex
from typing import List

import logging
log = logging.getLogger(__name__)
hdlr = logging.FileHandler(__name__ + '.log')
hdlr.setLevel(logging.DEBUG)
log.addHandler(hdlr)

class LogManager:

    # WIN_LOG = "C:\\Program Files\\Confer\\confer.log"
    WIN_LOG = 'C:\\dev\\hackathon\\confer.log'
    MAC_LOG = "/Applications/Confer.app/confer.log"

    def __init__(self):
        """
        :param log_file_name: Absolute path to log file
        """
        self.sensor_os = platform.system().lower()
        self.log_file_name = self.WIN_LOG
        if self.sensor_os == 'Darwin':
            self.log_file_name = self.MAC_LOG

        '''
        self.parser = LogParser()
        self.index = WhizIndex()
        self.date_time_index = WhizIndex()
        self.warn_error_index = WhizIndex()
        self.first_line_in_log = None
        self.last_index = 0
        self.error_count = 0
        self.warn_count = 0
        self.last_read_time = None
        self.log_thread = None
        self.update_index()
        '''

    def set_log(self, file_path: str):
        self.log_file_name = file_path

    def update_index(self):
        self.log_thread = threading.Timer(60.0, self.update_index)
        self.log_thread.start()
        log.info("Updating Index")
        if self.log_file_name is None:
            log.error("Log File Required")
            return
        if not os.path.exists(self.log_file_name):
            log.error("Log File does not exist")
            return
        if not self.first_line_is_equal():
            log.info("Re indexing Confer.log")
            self.clear_index()
            self.last_index = 0
        self.index_full_log()
        self.last_read_time = datetime.datetime.now()

    def index_full_log(self):
        with open(self.log_file_name) as log_file:
            for i, line in enumerate(log_file):
                if i is 0:
                    self.first_line_in_log = line
                if i < self.last_index:
                    continue
                self.last_index = i
                self.add_line_to_index(i, line)

    def add_line_to_index(self, line_index: int, line: str):
        line_info = self.parser.extract_info_from_line(line)
        for key in line_info.keys():
            if key is 'log_line':
                continue
            if key is 'date' or key is 'time':
                for info_item in line_info[key]:
                    self.date_time_index.add_line_for_value(new_key=info_item, new_line=line_index)
            elif key is 'warn' or key is 'error':
                self.warn_error_index.add_line_for_value(new_key=key, new_line=line_index)
            else:
                for info_item in line_info[key]:
                    self.index.add_line_for_value(new_key=info_item, new_line=line_index)

    def clear_index(self):
        self.index.clear()
        self.date_time_index.clear()
        self.first_line_in_log = None
        self.last_index = None

    def shutdown_log_thread(self):
        self.log_thread.cancel()

    def search_index(self, search_string, html=False):
        log_line_numbers = self.index.search(search_string)
        if not log_line_numbers:
            log_line_numbers = self.date_time_index.search(search_string)
        if not log_line_numbers:
            result = None
        else:
            result = self.get_lines_for_index_list(log_line_numbers, html=html)
        return result

    def search_log_file(self, search_string, html=False):
        lines = []
        with open(self.log_file_name) as log_file:
            for line in log_file:
                if search_string in line:
                    if html:
                        line = self.add_html_to_line(line)
                    lines.append(line)
        if len(lines) == 0:
            return None
        return lines

    def get_lines_for_index_list(self, index_list, html=False):
        lines = []
        with open(self.log_file_name) as log_file:
            for i, line in enumerate(log_file):
                if i in index_list:
                    if html:
                        line = self.add_html_to_line(line)
                    lines.append(line)
        return lines

    def add_html_to_line(self, log_line):
        log_line = '<div>{}</div>'.format(log_line)
        log_line = self.add_hash_search_links(log_line)
        return log_line

    def add_hash_search_links(self, log_line: str):
        hash_info = self.parser.extract_hash(log_line)
        if 'file_hash' in hash_info.keys():
            file_hash_list = hash_info['file_hash']
            for file_hash in file_hash_list:
                # log_line = log_line.replace(file_hash, "<a class='hashlink' href='/Search?search_string={0}' >{0}</a>".format(file_hash))
                log_line = self.add_tooltip(file_hash, log_line)
        if 'rep_hash' in hash_info.keys():
            rep_hash_list = hash_info['rep_hash']
            for rep_hash in rep_hash_list:
                log_line = self.add_tooltip(rep_hash, log_line)
        return log_line

    def add_tooltip(self, text: str, log_line: str):
        tool_tip = self.get_tooltip_for_rep(text)
        if not tool_tip:
            tool_tip = self.get_tooltip_for_hash(text)
        tool_tip_line = "<div class='whiztooltip'><a class='tooltiplink' href='/Search?search_string={0}'>{0}</a><span class='tooltiptext'>{1}</span></div>".format(text, tool_tip)
        log_line = log_line.replace(text, tool_tip_line)
        return log_line

    def get_tooltip_for_rep(self, text: str):
        tip = ''
        for rep_hash in  self.parser.reputation_hash.keys():
            if text == rep_hash:
                tip = self.parser.reputation_hash[text]
                break
        return tip

    def get_tooltip_for_hash(self, text: str):
        tip = ''
        for file_hash in self.parser.file_hash.keys():
            if text == file_hash:
                tip = self.parser.file_hash[text]
                break
        return tip

    def first_line_is_equal(self):
        if not self.first_line_in_log:
            return False

        with open(self.log_file_name, 'r') as f:
            first_line = f.readline()

        if self.first_line_in_log == first_line:
            return True
        return False

    def get_repuation_def(self, rep_hash):
        return self.parser.get_reputation_hash_def(rep_hash)

    def get_errors(self, html=False):
        log_line_numbers = self.warn_error_index.search('error')
        result = self.get_lines_for_index_list(log_line_numbers, html=html)
        return result

    def get_warnings(self, html=False):
        log_line_numbers = self.warn_error_index.search('warn')
        result = self.get_lines_for_index_list(log_line_numbers, html=html)
        return result

    def reduce_similar_errors(self, data: List[str], existing_errors: List[str] = None):
        unique_errors = []
        error_reg = {
            r'\(pid=(.*)\)': '',
            r'MSI.*.tmp': 'MSI.tmp'
        }
        errors = [x.rstrip("\n")[28:] for x in data]
        for error in errors:
            for key, value in error_reg.items():
                error = re.sub(key, value, error)

            unique_errors.append(error)

        if existing_errors:
            for existing in existing_errors:
                if existing in unique_errors:
                    unique_errors.remove(existing)

        unique_errors = {x: unique_errors.count(x) for x in unique_errors}
        return unique_errors
