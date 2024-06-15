from threading import Lock


def global_thread_safe(fn):
    lock = Lock()

    def wrapper(*args, **kwargs):
        with lock:
            return fn(*args, **kwargs)

    return wrapper
