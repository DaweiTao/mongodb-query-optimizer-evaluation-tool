import logging
import sys
import functools


# logger = logging.getLogger('experiment_logger')


def init_logger(log_file_path):
    logger = logging.getLogger('experiment_logger')
    logger.setLevel('DEBUG')
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%d/%m/%Y %I:%M:%S')

    # print log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    # persist log
    log_file_handler = logging.FileHandler(log_file_path)
    log_file_handler.setFormatter(log_formatter)
    logger.addHandler(log_file_handler)

    return logger


def logging_decorator(func=None):
    def log_decorator_info(func):
        @functools.wraps(func)
        def log_decorator_wrapper(*args, **kwargs):
            logger = logging.getLogger('experiment_logger')
            logger.info("- Enter function: {}".format(func.__name__))

            try:
                args_passed_in_function = [repr(a) for a in args]
                kwargs_passed_in_function = [f"{k}={v!r}" for k, v in kwargs.items()]
                formatted_arguments = ", ".join(args_passed_in_function + kwargs_passed_in_function)
                logger.info("Arguments: {}".format(formatted_arguments))
                value = func(*args, **kwargs)
                logger.info("Returned: {}".format(value))
                logger.info("- End function: {}".format(func.__name__))
            except:
                logger.error("Exception: {}".format(str(sys.exc_info()[1])))
                raise

            return value
        return log_decorator_wrapper

    if func is None:
        return log_decorator_info

    return log_decorator_info(func)
