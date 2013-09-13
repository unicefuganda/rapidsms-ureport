import datetime
from functools import wraps
import sys


def take_screenshot_on_failure(test):
    @wraps(test)
    def inner_decorator(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception:
            _, e, traceback = sys.exc_info()
            try:
                test_object = args[0]
                timestamp = datetime.datetime.now().isoformat().replace(':', '')
                filename = r'target/reports/functional-test/screenshots/failure_%s.png' % timestamp
                test_object.browser.driver.save_screenshot(filename)
                print r'Dumped screen shot of failure to [%s]' % filename
            except Exception, ex:
                print "Could not take screenshot: %s" % ex
            raise e, None, traceback
    return inner_decorator
