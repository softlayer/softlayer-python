"""
    SoftLayer.decoration
    ~~~~~~~~~~~~~~~~~~~~
    Handy decorators to use

    :license: MIT, see LICENSE for more details.
"""
from functools import wraps
import time


def retry(ex, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ex: the exception to check. may be a tuple of exceptions to check
    :type ex: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
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
                    msg = "%s, Retrying in %d seconds..." % (str(error), mdelay)
                    if logger:
                        logger.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
