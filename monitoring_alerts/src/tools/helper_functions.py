import os
import tempfile
from typing import Tuple

# Create a project-specific temporary directory
project_temp_dir = os.path.join(os.getcwd(), "temp")
os.makedirs(project_temp_dir, exist_ok=True)

# Set the new temporary directory
os.environ['TMPDIR'] = project_temp_dir
tempfile.tempdir = project_temp_dir


def get_evidently_html(evidently_object) -> Tuple[str, bytes]:
    """Returns the rendered EvidentlyAI report/metric as HTML and binary format"""
    try:
        # Use a more specific filename
        with tempfile.NamedTemporaryFile(
            mode='w+', delete=False, suffix='.html', dir=project_temp_dir
        ) as tmp:
            evidently_object.save_html(tmp.name)
            tmp_path = tmp.name

        # Read the file after it's closed
        with open(tmp_path, 'r', encoding='utf-8') as fh:
            html = fh.read()

        with open(tmp_path, 'rb') as fh:
            html_bytes = fh.read()

        # Clean up the temporary file
        os.unlink(tmp_path)

        return html, html_bytes

    except PermissionError as e:
        print(f"Permission error: {e}")
        print(f"Current user: {os.getlogin()}")
        print(f"Temp directory: {tempfile.gettempdir()}")
        raise

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
