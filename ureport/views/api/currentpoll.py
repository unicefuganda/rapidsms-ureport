from django.http import HttpResponse
from poll.models import Poll
from script.models import ScriptProgress, Script
from ureport.views.api.base import UReporterApiView


class ViewCurrentPoll(UReporterApiView):
    def get(self, request, *args, **kwargs):
        data = {}
        if self.contact_exists(self.connection):
            data['success'] = True
            data['poll'] = self.get_current_poll_for(self.connection.contact)
        else:
            data['success'] = True
            self.script_progress = self.get_script_progress(self.connection)
            step = self.get_current_step(self.script_progress)
            if step and step.poll:
                data['poll'] = self.get_data_from_poll(step.poll, True)
            elif step and step.message:
                data['poll'] = self.get_data_from_message(step.message)
                self.script_progress.moveon()
        return self.create_json_response(data)


    def format_date(self, start_date):
        return start_date.strftime(self.get_datetime_format()) if start_date else None

    def get_data_from_poll(self, poll, is_registration=False):
        return {"name": poll.name, "question": poll.question, "id": str(poll.id), "language": None,
                "start_date": self.format_date(poll.start_date), "end_date": self.format_date(poll.end_date),
                "type": poll.type,
                "question_voice": None, "is_registration": is_registration,
                "response_type": "allow_all" if poll.response_type == "a" else "allow_one",
                "default_response": poll.default_response, "default_response_voice": None}

    def get_current_poll_for(self, contact):
        try:
            poll = contact.polls.filter(start_date__isnull=False, end_date__isnull=True).latest("start_date")
        except Poll.DoesNotExist:
            return None
        return self.get_data_from_poll(poll)

    def get_script_progress(self, connection):
        script_progress_querylist = ScriptProgress.objects.filter(connection=connection,
                                                                  script__slug="ureport_autoreg2")
        if len(script_progress_querylist) > 0:
            script_progress = script_progress_querylist[0]
        else:
            script = Script.objects.get(slug="ureport_autoreg2")
            script_progress = ScriptProgress.objects.create(connection=connection, script=script)
            script_progress.start()
        return script_progress

    def get_current_step(self, script_progress):
        return script_progress.step

    def get_data_from_message(self, message):
        return {"id": None, "name": "Message", "question": message, "type": "none"}

    def post(self, request, *args, **kwargs):
        return HttpResponse("Method Not Allowed", status=405)
