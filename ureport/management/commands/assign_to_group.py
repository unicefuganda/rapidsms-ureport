from django.core.management.base import BaseCommand
from script.models import ScriptSession,Script
import traceback
from django.contrib.auth.models import Group
class Command(BaseCommand):

    def handle(self, **options):
        try:
            group_poll_responses=Script.objects.get(pk="ureport_autoreg").steps.get(order=1).poll.responses.all()
            gem=Group.objects.get(name="Girl Education Movement")
            world_vision=Group.objects.get(name="World Vision")
            bosco=Group.objects.get(name="BOSCO")
            msc=Group.objects.get(name="MSC")
            cou=Group.objects.get(name="Church of Uganda")
            catholic_secritariat=Group.objects.get(name="Catholic secritariat")
            groups={
                catholic_secritariat:["catholic",'secritariat'],
                world_vision:["world","vision"],
                gem:["gem"],
                bosco:["bosco"],
                msc:["muslim","supreme"],
                cou:["church"],
            }
            for response in group_poll_responses:
                txt=response.message.text.strip().lower()
                for group, word_list in groups.items( ):
                    for word in word_list:
                        if word in txt.split():
                            if group not in response.contact.groups.all():
                                response.contact.groups.add(group)
                                print "added contact with response " +txt+ "to " +str(group.name)


        except Exception, exc:
            print traceback.format_exc(exc)
