import logging
from mainsite.settings import DEBUG


LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("logger")
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(LOGGING_LEVEL)
logger.propagate = False
