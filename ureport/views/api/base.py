from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.generic import View
from rapidsms.models import Backend, Connection


class UReporterApiView(View):
    def parse_url_parameters(self, kwargs):
        self.backend_name = kwargs.get("backend")
        self.user_address = kwargs.get("user_address")

    def get_connection(self):
        backend = Backend.objects.get(name=self.backend_name)
        connection, connection_created = Connection.objects.get_or_create(identity=self.user_address, backend=backend)
        return connection


    def create_json_response(self, response_data, status_code=200):
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status_code)

    def get(self, request, *args, **kwargs):
        self.parse_url_parameters(kwargs)
        return HttpResponse("")

    def contact_exists(self, connection):
        return connection is not None and connection.contact is not None