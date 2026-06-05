import os
import pytest
from pathlib import Path
from bruno.config import BrunoSettings

@pytest.fixture
def temp_data_dir(tmp_path):
    os.environ["BRUNO_DATA_DIR"] = str(tmp_path)
    os.environ["OPENAI_API_KEY"] = "test-key"
    return tmp_path

@pytest.fixture
def settings(temp_data_dir):
    return BrunoSettings(data_dir=temp_data_dir, openai_api_key="test-key")
