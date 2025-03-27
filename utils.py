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


# def mac_addr(bytestring):
#     """Needs linux."""
#     return ':'.join('{:02x}'.format(piece) for piece in bytestring).upper()

