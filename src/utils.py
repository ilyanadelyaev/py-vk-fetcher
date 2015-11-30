import time
import functools

import progressbar


class EnumBase(type):
    def __iter__(cls):
        for attr, val in cls.iteritems():
            yield val

    def __getitem__(cls, item):
        try: 
            return getattr(cls, item)
        except AttributeError:
            raise KeyError("Enumerator '{}.{}' does not contain key {!r}".format(
                cls.__module__, cls.__name__, item 
            ))

    def iteritems(cls):
        for attr, val in cls.__dict__.iteritems():
            if attr.isupper():
                yield attr, val

    def val2str(cls, item):
        for attr, val in cls.iteritems():
            if val == item:
                return attr 
        raise ValueError("Enumerator '{}.{}' does not contain value {!r}".format(
            cls.__module__, cls.__name__, item 
        ))


def not_each_time(period):
    """
    Decorator. Performs call to a target function less frequently than it called -
    the function will be called only once per period specified.
    :param period:  Period in seconds, the function should NOT be called after last call.
    :return:        Decorator function.
    """
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            now = time.time()
            if not kwargs.pop('force', False) and _wrapper.last_called + period >= now:
                return
            _wrapper.last_called = now
            return func(*args, **kwargs)

        _wrapper.last_called = 0
        return _wrapper

    return _decorator



class ProgressBar(object):
    """ Generally used progress bar implementation. """

    def __init__(self, label, maxval):
        self.pb = progressbar.ProgressBar(
            widgets=[
                '{}: '.format(label),
                progressbar.Bar(), ' ', progressbar.Percentage(),
                #' | ', progressbar.FormatLabel('%(value)d/%(max)d'),
                #' | ', progressbar.Timer(),
                ' | ', progressbar.ETA(),
            ],
            maxval=maxval or 1
        ).start()

    @not_each_time(1)
    def update(self, val):
        self.pb.update(min(val, self.pb.maxval))

    def finish(self):
        self.pb.finish()
