from poll.models import Poll
from script.models import ScriptProgress, Script
from ureport.views.api.base import UReporterApiView


class ViewCurrentPoll(UReporterApiView):
    def get(self, request, *args, **kwargs):
        self.parse_url_parameters(kwargs)
        connection = self.get_connection()
        data = {}
        if self.contact_exists(connection):
            data['success'] = True
            data['poll'] = self.get_current_poll_for(connection.contact)
        else:
            data['success'] = True
            self.script_progress = self.get_script_progress(connection)

            #if not registered
        #   is there a script progress object ?
        #   if there is ? is the current step a message , question or email
        #   if there is no ? create the script progress and send out the first step
        #DONE
        return self.create_json_response(data)

    def get_current_poll_for(self, contact):
        try:
            poll = contact.polls.filter(start_date__isnull=False, end_date__isnull=True).latest("start_date")
        except Poll.DoesNotExist:
            return None
        return {"name": poll.name, "question": poll.question}

    def get_script_progress(self, connection):
        script_progress_querylist = ScriptProgress.objects.filter(connection=connection,
                                                                  script__slug="ureport_autoreg2")
        if len(script_progress_querylist) > 0:
            script_progress = script_progress_querylist[0]
        else:
            script = Script.objects.get(slug="ureport_autoreg2")
            script_progress = ScriptProgress.objects.create(connection=connection, script=script)
        return script_progress

    def get_next_step(self, script_progress):
        return script_progress.get_next_step()