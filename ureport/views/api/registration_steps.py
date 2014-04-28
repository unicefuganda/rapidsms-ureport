import json
from django.db.models import Q
from script.models import Script
from django.http import HttpResponse
import settings
from ureport.views.api.base import BasicAuthenticationView


class RegistrationStepsView(BasicAuthenticationView):

    def get(self, request, *args, **kwargs):
        registration_scripts = self.get_registration_scripts()
        registration_steps = self.get_script_steps(registration_scripts)
        step_messages = self.get_step_strings(registration_steps)

        data = {"steps": step_messages}
        return HttpResponse(json.dumps(data), content_type="application/json", status=200)

    def get_script_steps(self, scripts):
        steps = []
        for script in scripts:
            steps.extend(script.steps.all())
        return steps

    def get_step_strings(self, registration_steps):
        step_messages = set()
        for step in registration_steps:
            if step and step.poll:
                step_messages.add(step.poll.question)
            else:
                step_messages.add(step.message)
        return list(step_messages)

    def get_registration_scripts(self):
        return Script.objects.filter(self.get_registration_scripts_query())

    def get_registration_scripts_query(self):
        default_scripts = ['ureport_autoreg2', 'ureport_autoreg_luo2', 'ureport_autoreg_kdj']
        registration_scripts_name = getattr(settings, 'REGISTRATION_SCRIPTS', default_scripts)
        script_iteration = iter(registration_scripts_name)
        query = Q(slug=script_iteration.next())
        for script_name in script_iteration:
            query |= Q(slug=script_name)
        return query