import timeit

def time_action(func):
    def wrapper_func(*args, **kwargs):
        t1 = timeit.default_timer()
        retval = func(*args, **kwargs)
        t2 = timeit.default_timer()
        print("Time taken to run {}: {}".format(func.__name__, format(t2 - t1, '.8f')))
        return retval
    return wrapper_func