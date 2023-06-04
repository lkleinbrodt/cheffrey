import logging

def create_logger(name):
    # Create a logger instance
    logger = logging.getLogger(name)
    # logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger