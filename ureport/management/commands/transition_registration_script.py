import urllib
import urllib2
import time

from django.core.management import BaseCommand, call_command

from rapidsms.models import Connection

from rapidsms_httprouter.models import Message
from script.models import ScriptProgress
from script.utils.outgoing import check_progress


class Command(BaseCommand):
    def get_full_url(self, message):
        url = "http://%s/router/receive" % self.server_ip

        values = {"sender": self.sender_number, "backend": "console", "message": message}
        url_values = urllib.urlencode(values)
        full_url = url + '?' + url_values

        return full_url

    def send_sms(self, message):
        urllib2.urlopen(self.get_full_url(message))

    def prompt_response(self):
        return raw_input("Reply> ")

    def get_sms(self):
        return Message.objects.filter(connection=self.user_connection, direction="O").order_by("-id")[0]

    def start_interactive_console(self):

        while True:
            self.trigger_next_step()

            message = self.get_sms()
            print message.text

            response = self.prompt_response()
            self.send_sms(response)

            time.sleep(2)

    def trigger_next_step(self):
        self.script_progress_object = ScriptProgress.objects.get(connection=self.user_connection)
        next_step = self.script_progress_object.get_next_step()
        next_step.start_offset = 0
        next_step.save()
        check_progress(next_step.script)

    def update_script_progress_object(self):
        self.script_progress_object = ScriptProgress.objects.get(connection=self.user_connection)

    def transition_through_first_step(self):
        self.update_script_progress_object()
        step = self.script_progress_object.step
        step.giveup_offset = 0
        step.save()
        check_progress(self.script_progress_object.script)

    def send_join_message(self, args):
        self.sender_number = int(args[0])
        self.send_sms("JOIN")
        self.user_connection = Connection.objects.get(identity=self.sender_number)
        self.update_script_progress_object()
        check_progress(self.script_progress_object.script)

    def handle(self, *args, **options):
        if len(args) < 1:
            print("usage: python manage.py transition_registration_script <sender number> [server ip (2.2.2.2)]")
            exit(-1)

        if len(args) == 2:
            self.server_ip = args[1]
        else:
            self.server_ip = "2.2.2.2"

        try:
            self.send_join_message(args)

            self.transition_through_first_step()

            print "starting session as [%s]" % self.sender_number

            self.start_interactive_console()


        except Exception:
            self.update_script_progress_object()
            check_progress(self.script_progress_object.script)
            call_command('loaddata', "0004_migration_initial_data", interactive=True)
            print("Congratulations! Registration complete. Cya.")
            exit()
