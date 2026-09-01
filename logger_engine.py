import logging
import os
from paths import writable_dir

LOG_DIR = writable_dir("logs")
LOG_PATH = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def log_info(msg):
    logging.info(msg)


def log_error(msg):
    logging.error(msg)


def get_log_path():
    return LOG_PATH
