import json
import logging
import os
from datetime import datetime, timezone

from flask import Flask, jsonify

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "python-app")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "/var/log/python-app")
PORT = int(os.getenv("PORT", "5000"))


def setup_logging() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(name)s - %(message)s")

    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)


setup_logging()
log = logging.getLogger(APP_NAME)


@app.get("/")
def root():
    payload = {
        "service": APP_NAME,
        "language": "python",
        "message": "Hello from Flask",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    log.info("GET / %s", json.dumps(payload))
    return jsonify(payload), 200


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

