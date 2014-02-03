import base64


class TestBasicAuthMixin(object):
    def http_auth(self, username, password):
        credentials = base64.encodestring('%s:%s' % (username, password)).strip()
        auth_string = 'Basic %s' % credentials
        return auth_string

    def get_auth_headers(self):
        extra = {
            'HTTP_AUTHORIZATION': self.http_auth('test', 'nakulabye')
        }
        return extra