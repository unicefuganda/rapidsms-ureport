from django.core.management.base import BaseCommand
from script.models import *
from poll.models import *

class Command(BaseCommand):

    def handle(self, **options):
        script = Script.objects.create(
                slug="ureport_autoreg",
                name="uReport autoregistration script",
        )
        user = User.objects.get(username="ureport")
        script.sites.add(Site.objects.get_current())
        script.steps.add(ScriptStep.objects.create(
            script=script,
            message="Welcome to U-report!, U-report is a FREE service that helps youth speak out on issues in their communities using SMS. SPEAK UP and BE HEARD! ",
            order=0,
            rule=ScriptStep.WAIT_MOVEON,
            start_offset=0,
            giveup_offset=60,
        ))
        poll = Poll.create_freeform("youthgroup", "Now we are going to ask a few questions to finish your registration as a U-reporter. Please reply with the name of your PAYAM", "", [], user)
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=poll,
            order=1,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=0,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        script.steps.add(ScriptStep.objects.create(
            script=script,
            message="Ureport is a FREE SMS text message system that is sent to your phone.  Ureport is sponsored by UNICEF and other partners.",
            order=2,
            rule=ScriptStep.WAIT_MOVEON,
            start_offset=60,
            giveup_offset=60,
        ))
        poll4 = Poll.create_custom('district',"contactdistrict", "Its important to know which District you'll be reporting on so we can work together to try & resolve issues in your community!Reply ONLY with your district.", "", [], user)
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=poll4,
            order=3,
            rule=ScriptStep.STRICT_MOVEON,
            start_offset=0,
            retry_offset=86400,
            num_tries=1,
            giveup_offset=86400,
        ))
        script.steps.add(ScriptStep.objects.create(
            script=script,
            message="Ureport gives you a chance to speak out on issues in your community & share opinions with youth around Uganda!Best responses&results shared through the media!",
            order=4,
            rule=ScriptStep.WAIT_MOVEON,
            start_offset=60,
            giveup_offset=60,
        ))
        poll2 = Poll.create_freeform("contactname", "Best responses may be shared!Send us your name,or if you prefer a nickname so we can give u recognition for good replies by sharing them in the media!", "", [], user)
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=poll2,
            order=5,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=60,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        poll5 = Poll.create_numeric("contactage", "What is your AGE? Please reply with only the number", "", [], user)
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=poll5,
            order=6,
            rule=ScriptStep.STRICT_MOVEON,
            num_tries=1,
            start_offset=60,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        poll3 = Poll.create_freeform("contactgender", "Are you male or female?  Type F for female, and M for Male", "", [], user)
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=poll3,
            order=7,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=60,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        poll3.categories.create(name='male')
        poll3.categories.get(name='male').rules.create(
            regex=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['m','mal','male','ma'])),
            rule_type=Rule.TYPE_REGEX,
            rule_string=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['m','mal','male','ma'])))
        poll3.categories.create(name='female')
        poll3.categories.get(name='female').rules.create(
            regex=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['f','fem','female','fe'])),
            rule_type=Rule.TYPE_REGEX,
            rule_string=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['f','fem','female','fe'])))

        poll9 = Poll.create_location_based("contactvillage", "Which village in the district will you be reporting from? Please respond ONLY with the name of your village.", "", [], user)
        script.steps.add(ScriptStep.objects.create(
            script=script,
            poll=poll9,
            order=8,
            rule=ScriptStep.RESEND_MOVEON,
            num_tries=1,
            start_offset=0,
            retry_offset=86400,
            giveup_offset=86400,
        ))
        script.steps.add(ScriptStep.objects.create(
            script=script,
            message="CONGRATULATIONS!!! You are now a registered member of U-report! With U-report, Your Voice counts! We will send the first U-report Poll soon!",
            order=9,
            rule=ScriptStep.WAIT_MOVEON,
            start_offset=60,
            giveup_offset=0,
        ))
