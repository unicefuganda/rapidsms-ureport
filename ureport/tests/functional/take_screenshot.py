import datetime
from functools import wraps


def take_screenshot_on_failure(test):
    @wraps(test)
    def inner_decorator(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception, e:
            try:
                test_object = args[0]
                timestamp = datetime.datetime.now().isoformat().replace(':', '')
                filename = r'target/reports/functional-test/screenshots/failure_%s.png' % timestamp
                test_object.browser.driver.save_screenshot(filename)
                print r'Dumped screen shot of failure to [%s]' % (filename)
            except Exception, ex:
                print ex.message
            raise Exception(e)
    return inner_decorator