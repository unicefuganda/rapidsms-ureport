import base64
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import simplejson as json
from django.views.generic import View
from rapidsms.models import Backend, Connection

UREPORT_JSON_API_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class BasicAuthenticationView(View):
    def validate_credentials(self, username, password):
        api_users = getattr(settings, "UREPORT_JSON_API_USERS", {})
        if username in api_users and api_users[username] == password:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == "basic":
                    try:
                        uname, passwd = base64.b64decode(auth[1]).split(':')
                        if not self.validate_credentials(uname, passwd):
                            return HttpResponse("Not Authorized", status=401)
                    except TypeError:
                        return HttpResponse("Not Authorized", status=401)
            else:
                return HttpResponse("Not Authorized", status=401)
        else:
            return HttpResponse("Not Authorized", status=401)
        return super(BasicAuthenticationView, self).dispatch(request, *args, **kwargs)


class UReporterApiView(BasicAuthenticationView):
    def parse_url_parameters(self, kwargs):
        self.backend_name = kwargs.get("backend")
        self.user_address = kwargs.get("user_address")
        if kwargs.get("poll_id"):
            self.poll_id = kwargs.get("poll_id")

    def get_backend(self):
        backend = Backend.objects.get(name=self.backend_name)
        return backend

    def get_connection(self):
        connection, connection_created = Connection.objects.get_or_create(identity=self.user_address,
                                                                          backend=self.backend)
        return connection


    def create_json_response(self, response_data, status_code=200):
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status_code)

    def get(self, request, *args, **kwargs):
        raise NotImplementedError("Define in subclass")

    def post(self, request, *args, **kwargs):
        raise NotImplementedError("Define in subclass")

    def contact_exists(self, connection):
        return connection is not None and connection.contact is not None

    def get_datetime_format(self):
        return getattr(settings, "UREPORT_JSON_API_DATETIME_FORMAT", UREPORT_JSON_API_DATETIME_FORMAT)

    def dispatch(self, request, *args, **kwargs):
        self.parse_url_parameters(kwargs)
        try:
            self.backend = self.get_backend()
        except Backend.DoesNotExist:
            raise Http404()
        self.connection = self.get_connection()
        return super(UReporterApiView, self).dispatch(request, *args, **kwargs)


class UReportPostApiViewMixin(object):
    def get_json_data(self, request):
        json_content = request.raw_post_data
        data_from_json = json.loads(json_content)
        return data_from_json

    def get(self, request, *args, **kwargs):
        return HttpResponse("Method Not Allowed", status=405)


