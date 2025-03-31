from timeit import default_timer as timer

def timefunc(func):
    """Allows timing of a function at runtime."""
    
    def inner(*args, **kwargs):
        start = timer()
        results = func(*args, **kwargs)
        end = timer()
        message = '{} took {} seconds'.format(func.__name__, end - start)
        print(message)
        return results
    return inner

import os
import time

def setup_logger(log_dir):
    """Sets up a logger that writes to a file."""

    path = f"logs/{log_dir}"
    if not os.path.exists(path):
        os.makedirs(path)
    log_filename = time.strftime(f"{log_dir}_%Y-%m-%d.txt", time.gmtime())
    log_filepath = os.path.join(path, log_filename)
    return log_filepath
    
def log_message(log_filepath, message):
    """Write a message to a logger file."""
    timestamp = time.strftime("%H:%M:%S", time.gmtime())
    with open(log_filepath, "a") as log_file:
        log_file.write(f"{timestamp}: " + message + "\n")
    
