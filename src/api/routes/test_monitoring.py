import logging


def test():

    logger = logging.getLogger(__name__)

    logger.info("Hello world")
    logger.info("With context", extra={"user_id": "123", "action": "login"})
