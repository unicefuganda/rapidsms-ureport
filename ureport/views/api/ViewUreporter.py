import django.utils.simplejson as json
from django.http import HttpResponse, Http404
from django.views.generic import View
from rapidsms.models import Backend, Connection


class ViewUreporter(View):
    def parse_url_parameters(self, kwargs):
        self.backend_name = kwargs.get("backend")
        self.user_address = kwargs.get("user_address")

    def get(self, request, *args, **kwargs):
        self.parse_url_parameters(kwargs)
        contact = self.get_contact()
        response_data = {u"success": True, "user": contact}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def post(self, request, *args, **kwargs):
        raise Http404()

    def get_contact(self):
        contact_data = {"id": "", "language": "", "registered": False}
        backend, backend_created = Backend.objects.get_or_create(name=self.backend_name)
        try:
            connection = Connection.objects.get(identity=self.user_address, backend=backend)
            if (connection.contact):
                contact_data["id"] = connection.contact.id
                contact_data["registered"] = True
                contact_data["language"] = connection.contact.language
        except Connection.DoesNotExist:
            pass
        return contact_data

