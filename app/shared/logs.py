import logging


def initialize():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%H:%M:%S',
        format='%(name)-12s | [%(levelname)s] %(asctime)s.%(msecs)03d %(message)s'
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
