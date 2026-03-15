import os
import tempfile
from tools.testscope.api import analyze, _parse_log


def test_parse_log():
    """Test the raw log parser."""
    mock_log = (
        "2023-10-01 12:00:00 INFO Initializing system...\n"
        "2023-10-01 12:00:01 DEBUG RRC Setup initiated.\n"
        "2023-10-01 12:00:02 INFO Registration Accept received.\n"
        "2023-10-01 12:00:03 ERROR FAILURE: Connection timeout.\n"
    )

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(mock_log)
        tmp_path = f.name

    try:
        events = _parse_log(tmp_path)
        assert len(events) == 4
        assert events[0] == "OTHER"
        assert events[1] == "RRC_SETUP"
        assert events[2] == "REGISTRATION_SUCCESS"
        assert events[3] == "FAILURE"
    finally:
        os.remove(tmp_path)


def test_analyze_kpis():
    """Test KPI calculation via the analyze API."""
    mock_log = (
        "RRC Setup\n"
        "Registration Accept\n"
        "PDU Session established\n"
        "ERROR Generic FAILURE during handover\n"
        "Some random info line\n"
    )

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(mock_log)
        tmp_path = f.name

    try:
        result = analyze(tmp_path)

        assert result.tool_name == "testscope"
        assert result.total_events == 4  # OTHER is ignored in metrics
        assert result.failed == 1
        assert result.kpis["rrc_setups"] == 1
        assert result.kpis["registrations"] == 1
        assert result.kpis["pdu_sessions"] == 1
        # Success rate: (total - failures) / total = 3 / 4 = 75.0%
        assert result.success_rate == 75.0

        # Verify the exact failures
        assert "Generic Failure Detected" in result.issues

    finally:
        os.remove(tmp_path)
