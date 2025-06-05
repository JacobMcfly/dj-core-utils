import logging
from pythonjsonlogger import jsonlogger


def configure_logging(service_name: str) -> logging.Logger:
    """Configure structured logging for the service"""
    logger = logging.getLogger(service_name)

    if logger.handlers:  # Avoid multiple handlers
        return logger

    handler = logging.StreamHandler()
    format = (
        '%(asctime)s %(levelname)s %(name)s %(message)s '
        '%(pathname)s %(lineno)d'
    )
    formatter = jsonlogger.JsonFormatter(format)

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
