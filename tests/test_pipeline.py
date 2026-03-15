import os
import tempfile
from ttt.pipeline import discover_log_files

def test_discover_log_files():
    """Test that discover_log_files finds only .log and .txt files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy files
        log_file = os.path.join(tmpdir, "test_file.log")
        txt_file = os.path.join(tmpdir, "test_data.txt")
        csv_file = os.path.join(tmpdir, "test_results.csv")
        
        for f in [log_file, txt_file, csv_file]:
            with open(f, "w") as file:
                file.write("dummy content")
        
        files = discover_log_files(tmpdir)
        
        assert len(files) == 2
        assert log_file in files
        assert txt_file in files
        assert csv_file not in files
