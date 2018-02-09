from core.log_manager import LogManager


def test_full_index():
    manager = LogManager()
    assert manager.index
    assert manager.date_time_index
    assert manager.first_line_in_log == '02/08/18 10:10:49: 1f48     SvcReportStatus: service not allowed to stop\n'
    assert manager.last_index == 34061

    manager.clear_index()

    assert manager.first_line_in_log is None
    assert manager.last_index is None
