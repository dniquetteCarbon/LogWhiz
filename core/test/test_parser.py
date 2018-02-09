from core.log_parser import LogParser


def test_hash_parsing():
    parser = LogParser()
    line = '02/08/18 10:10:49: 8dc      DbAddRepSrcTableRecord: hash 0xadadfa0d: reputation(Pre-existing) is 0x00800000'
    info = parser.extract_info_from_line(line)
    assert info