from typing import Literal
import os
import tempfile
import requests
import zipfile
import re
from omop_provisioner.log import get_logger
import shutil
from pathlib import Path

log = get_logger()


class AthenaVocabFileHandler:
    def __init__(self, source: str):
        log.debug(f"AthenaVocabFileHandler source={source}")
        self.result_path = None
        self.temp_dir_download = None
        self.temp_dir_unzip = None
        if source is None:
            return
        self.source = source
        source_type = self._classify_path(source)
        zip_file = None

        if source_type == "url":
            self.temp_dir_download = tempfile.mkdtemp()
            log.info(f"Download Athena Vocab zip from {source}")
            zip_file = self._download_zip(self.temp_dir_download)
        elif source_type == "file":
            log.info(f"Try to extract Athena Vocabulary from zip file {source}")
            zip_file = source
        elif source_type == "dir":
            log.info(f"Assuming Athena vocabulary in directory {source}")
            self.result_path = source
        elif source_type is None:
            raise ValueError(
                f"'{source}' is not valid source for athena vocabulary. Its not an url, zip file or an existing directory. Maybe you need to mount the path into docker?"
            )
        if zip_file is not None:
            self.temp_dir_unzip = tempfile.mkdtemp()
            log.info(f"Unzip Athena Vocab zip from {zip_file}")
            self.result_path = self._extract_zip(zip_file, self.temp_dir_unzip)
        # sanity check
        if not self._contains_csv(self.result_path):
            log.warning(
                f"Could not extraxt/find any CSVs from '{source}'. No Vocabulary will be loaded. Maybe check setting 'VOCABULARY_SOURCE'"
            )
            self.result_path = None
            return
        log.info(f"Athena Vocab available at {self.result_path}")

    def get_vocab_csvs_path(self) -> Path | None:
        if self.result_path:
            return Path(self.result_path)
        return None

    def clean_up(self):
        if self.temp_dir_download:
            shutil.rmtree(self.temp_dir_download)
        if self.temp_dir_unzip:
            shutil.rmtree(self.temp_dir_unzip)

    def _classify_path(self, path: str) -> Literal["url", "file", "dir"] | None:
        """
        Classifies a given path as a URL, a local file, or a local directory.

        :param path: The string to classify
        :return: One of "URL", "Local File", "Local Directory", or "Unknown"
        """
        # Check if the path is a URL
        url_regex = re.compile(r"^(https?|ftp)://")
        if url_regex.match(path):
            return "url"

        # Expand user home (~) and environment variables
        expanded_path = os.path.expanduser(os.path.expandvars(path))
        log.debug(f"expanded_path {expanded_path}")
        log.debug(f"os.path.isfile(expanded_path):{os.path.isfile(expanded_path)}")
        log.debug(f"os.path.isdir(expanded_path):{os.path.isdir(expanded_path)}")
        # Check if the path is a local file
        if os.path.isfile(expanded_path):
            return "file"

        # Check if the path is a local directory
        if os.path.isdir(expanded_path):
            return "dir"

        return None

    def _download_zip(self, target):
        """Downloads the ZIP file from the URL to a temporary file."""
        response = requests.get(self.source, stream=True)
        if response.status_code == 200:
            zip_path = os.path.join(target, "downloaded.zip")
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return zip_path
        else:
            raise Exception(
                f"Failed to download file from {self.source}: {response.status_code}"
            )

    def _extract_zip(self, zip_path, target):
        """Extracts the ZIP file to the temporary directory."""
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(target)
        return target

    def _contains_csv(self, directory: str) -> bool:
        """Check if a directory contains at least one CSV file."""
        if not os.path.isdir(directory):
            raise ValueError(f"'{directory}' is not a valid directory")

        return any(file.lower().endswith(".csv") for file in os.listdir(directory))
