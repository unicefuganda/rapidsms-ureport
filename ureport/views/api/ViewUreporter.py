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
        status_code = 200
        response_data = {"success": True}
        if not contact["registered"]:
            response_data["success"] = False
            response_data["reason"] = "Ureporter not found"
            status_code = 404
        else:
            response_data["user"] = contact
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status_code)

    def post(self, request, *args, **kwargs):
        raise Http404()

    def get_contact(self):
        contact_data = {"language": "", "registered": False}
        backend, backend_created = Backend.objects.get_or_create(name=self.backend_name)
        try:
            connection = Connection.objects.get(identity=self.user_address, backend=backend)
            if (connection.contact):
                contact_data["registered"] = True
                contact_data["language"] = connection.contact.language
        except Connection.DoesNotExist:
            pass
        return contact_data

