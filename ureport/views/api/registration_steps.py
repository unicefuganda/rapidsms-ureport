import json
from django.db.models import Q
from script.models import Script
from django.http import HttpResponse
import settings
from ureport.views.api.base import BasicAuthenticationView
from poll.models import gettext_db


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
        registration_script_names = self.get_registration_script_name()
        for step in registration_steps:
            if step and step.poll:
                language = registration_script_names[step.script.slug]
                step_messages.add(gettext_db(step.poll.question, language))
            else:
                step_messages.add(step.message)
        return list(step_messages)

    def get_registration_scripts(self):
        return Script.objects.filter(self.get_registration_scripts_query())

    def get_registration_scripts_query(self):
        registration_scripts_name = self.get_registration_script_name()
        script_iteration = iter(registration_scripts_name)
        query = Q(slug=script_iteration.next())
        for script_name in script_iteration:
            query |= Q(slug=script_name)
        return query

    def get_registration_script_name(self):
        default_scripts = {'ureport_autoreg2': 'en', 'ureport_autoreg_luo2': 'ach', 'ureport_autoreg_kdj': 'kdj'}
        return getattr(settings, 'REGISTRATION_SCRIPTS', default_scripts)
