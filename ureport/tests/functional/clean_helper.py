import urllib
import urllib2
from django.conf import settings


def login_as_admin(username, password):
    login_url = build_url('/accounts/login/')
    cookies = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookies)
    urllib2.install_opener(opener)
    opener.open(login_url)
    try:
        token = [x.value for x in cookies.cookiejar if x.name == 'csrftoken'][0]
    except IndexError:
        return False, "no csrftoken"
    params = dict(username=username, password=password, this_is_the_login_form=True, csrfmiddlewaretoken=token)
    encoded_params = urllib.urlencode(params)
    opener.open(login_url, encoded_params)
    return opener

def build_url(url):
    return "%s%s" % (settings.TEST_SERVER_URL, url)

def post(opener, url, values={}):
    data =  urllib.urlencode(values)
    opener.open(url, data)