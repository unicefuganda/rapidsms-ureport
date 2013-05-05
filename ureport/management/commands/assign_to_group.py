from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from script.models import ScriptSession,Script
import traceback
import re
from django.contrib.auth.models import Group, User
from script.utils.handling import find_closest_match

class Command(BaseCommand):

    def handle(self, **options):
        try:
            group_poll_responses=Script.objects.get(pk="ureport_autoreg").steps.get(order=1).poll.responses.all()
            gem=Group.objects.get(name="GEM")
            world_vision=Group.objects.get(name="World Vision")
            bosco=Group.objects.get(name="BOSCO")
            msc=Group.objects.get(name="MSC")
            cou=Group.objects.get(name="Church of Uganda")
            catholic_secritariat=Group.objects.get(name="Catholic secretariat")
            groups={
                catholic_secritariat:["catholic",'secritariat'],
                world_vision:["world","vision"],
                gem:["gem","eduction movement"],
                bosco:["bosco"],
                msc:["muslim","supreme"],
                cou:["church"],
            }
            for response in group_poll_responses:
                txt=response.message.text.strip().lower()

                matched=False

                for group, word_list in groups.items():
                    for word in word_list:
                        if word in txt.split():
                            if response.contact and group not in response.contact.groups.all():
                                response.contact.groups.add(group)
                                print "handled"
                                print txt
                                print response.contact.groups.all()
                                matched=True
                #get fuzzier
                if not matched:
                    for g in re.findall(r'\w+', txt):
                        group = find_closest_match(g, Group.objects)
                        if group and group in User.objects.get(username="ureport").groups.all():
                            if response.contact and  group not in response.contact.groups.all():
                                response.contact.groups.add(group)
                                print "handled"
                                print txt
                                print response.contact.groups.all()

                        


                            
        except Exception, exc:
            print traceback.format_exc(exc)
