import json
from poll.models import Poll
from script.models import ScriptProgress, Script
from django.http import HttpResponse
from ureport.views.api.base import BasicAuthenticationView


class RegistrationStepsView(BasicAuthenticationView):

    def get(self, request, *args, **kwargs):
        registration_script = self.get_registration_script()
        registration_steps = self.get_script_steps(registration_script)
        step_messages = self.get_step_strings(registration_steps)

        data = {"steps": step_messages}
        return HttpResponse(json.dumps(data), content_type="application/json", status=200)

    def get_registration_script(self):
        scripts = Script.objects.filter(slug="ureport_autoreg2")
        return scripts[0]

    def get_script_steps(self, script):
        return script.steps.all()

    def get_step_strings(self, registration_steps):
        step_messages = []
        for step in registration_steps:
            if step and step.poll:
                step_messages.append(step.poll.question)
            else:
                step_messages.append(step.message)
        return step_messages