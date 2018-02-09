import logging
log = logging.getLogger(__name__)


class WhizIndex:

    def __init__(self):
        self.index = {}

    def add_line_for_value(self, new_key: str, new_line: int):
        for key in self.index.keys():
            if key == new_key:
                if new_line not in self.index[key]:
                    self.index[key].append(new_line)
                return

        self.index[new_key] = [new_line]

    def get_lines_for_value(self, key):
        try:
            lines = self.index[key]
        except KeyError as e:
            log.warning('Key does not exist in index: %s', key)
            return []

    def clear(self):
        self.index.clear()

    def search(self, search_string):
        for key in self.index.keys():
            if search_string in key:
                return self.index[key]
        return None
