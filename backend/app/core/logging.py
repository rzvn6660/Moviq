import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Quiet noisy third-party loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


logger = logging.getLogger("moviq")
