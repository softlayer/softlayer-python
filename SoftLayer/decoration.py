"""
    SoftLayer.decoration
    ~~~~~~~~~~~~~~~~~~~~
    Handy decorators to use

    :license: MIT, see LICENSE for more details.
"""
from functools import wraps
from random import randint
from time import sleep

from SoftLayer import exceptions

RETRIABLE = (
    exceptions.ServerError,
    exceptions.ApplicationError,
    exceptions.RemoteSystemError,
    exceptions.TransportError
)


def retry(ex=RETRIABLE, tries=4, delay=5, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ex: the exception to check. may be a tuple of exceptions to check
    :param tries: number of times to try (not retry) before giving up
    :param delay: initial delay between retries in seconds.
        A random 0-5s will be added to this number to stagger calls.
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :param logger: logger to use. If None, print
    """
    def deco_retry(func):
        """@retry(arg[, ...]) -> true decorator"""

        @wraps(func)
        def f_retry(*args, **kwargs):
            """true decorator -> decorated function"""
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except ex as error:
                    sleeping = mdelay + randint(0, 5)
                    msg = "%s, Retrying in %d seconds..." % (str(error), sleeping)
                    if logger:
                        logger.warning(msg)
                    sleep(sleeping)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
