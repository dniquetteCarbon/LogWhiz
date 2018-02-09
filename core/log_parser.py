import re

HASH_REG = r'(0x[a-zA-Z0-9]{8})'
DATE_REG = r'(\d+/\d+/\d+)'
TIME_REG = r'([0-9]{2}:[0-9]{2}:[0-9]{2})'

class LogParser:

    reputation_hash = {
        '0x00000001': 'SI_PROPERTY_BIT_RESOLVING',
        '0x00000002': 'SI_PROPERTY_BIT_COMPROMISED',
        '0x00000004': 'SI_PROPERTY_BIT_DLP',
        '0x00000100': 'SI_PROPERTY_BIT_IGNORE',
        '0x00000200': 'SI_PROPERTY_BIT_WHITE',
        '0x00000400': 'SI_PROPERTY_BIT_ADAPTIVE',
        '0x00000800': 'SI_PROPERTY_BIT_PUA',
        '0x00001000': 'SI_PROPERTY_BIT_ADWARE',
        '0x00002000': 'SI_PROPERTY_BIT_HEURISTIC',
        '0x00004000': 'SI_PROPERTY_BIT_SUSPECT_MALWARE',
        '0x00008000': 'SI_PROPERTY_BIT_KNOWN_MALWARE',
        '0x00010000': 'SI_PROPERTY_BIT_ADMIN_RESTRICT',
        '0x00020000': 'SI_PROPERTY_BIT_ADMIN_BLOCKED',
        '0x00040000': 'SI_PROPERTY_BIT_NOT_LISTED',
        '0x00080000': 'SI_PROPERTY_BIT_COMMON',
        '0x00100000': 'SI_PROPERTY_BIT_GREY',
        '0x00200000': 'SI_PROPERTY_BIT_NOT_COMP_WHITE',
        '0x00400000': 'SI_PROPERTY_BIT_COMPANY_WHITE',
        '0x00800000': 'SI_PROPERTY_BIT_LOCAL_WHITE',
        '0x01000000': 'SI_PROPERTY_BIT_RESERVED3',
        '0x02000000': 'SI_PROPERTY_BIT_RESERVED4',
        '0x04000000': 'SI_PROPERTY_BIT_RESERVED5',
        '0x08000000': 'SI_PROPERTY_BIT_RESERVED6',
        '0x80000000': 'SI_PROPERTY_BIT_NOT_SUPPORTED'
    }

    def get_reputation_hash_def(self, hash):
        if hash in self.reputation_hash.keys():
            return self.reputation_hash[hash]
        return 'Not a valid reputation hash'

    def extract_info_from_line(self, log_line: str):
        line_info = {'log_line': log_line}
        line_info = self.extract_hash(log_line, line_info)
        line_info = self.extract_date_time(log_line, line_info)
        return line_info

    def extract_hash(self, log_line: str, line_info):
        hash_matched = re.findall(HASH_REG, log_line)
        if hash_matched:
            file_hash = []
            rep_hash = []
            for hash in hash_matched:
                if hash in self.reputation_hash.keys():
                    rep_hash.append(hash)
                else:
                    file_hash.append(hash)
            line_info['file_hash'] = file_hash
            line_info['rep_hash'] = rep_hash
        return line_info

    def extract_date_time(self, log_line: str, line_info):
        date_match = re.findall(DATE_REG, log_line)
        time_match = re.findall(TIME_REG, log_line)
        if date_match:
            line_info['date'] = date_match
        if time_match:
            line_info['time'] = time_match
        return line_info

