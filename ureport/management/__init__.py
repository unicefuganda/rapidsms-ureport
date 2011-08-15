from django.db.models import get_models
from script import models as script_app
from poll import models as poll_app
from django.contrib.sites import models as sites_app
from authsites import models  as authsites_app
from django.contrib.auth import models as auth_app
from script.models import *
from poll.models import *
from django.conf import settings
models_created = []

def create_auto_reg_script(app, created_models, verbosity, **kwargs):
    """ callback to post_syncdb signal to create auto_reg  script """

    global models_created
    models_created=models_created+get_models(app)
    required_models = get_models(script_app) + get_models(poll_app) + get_models(auth_app)
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        required_models = required_models + get_models(sites_app) + get_models(authsites_app)
    for model in  required_models:
        if not model in models_created:
            return
    else:
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            try:
                site=Site.objects.get_current()
            except Site.DoesNotExist:
                site=Site.objects.create(pk=settings.SITE_ID, domain='ureport.ug')
        script, created = Script.objects.get_or_create(
                slug="ureport_autoreg",
                name="uReport autoregistration script",
                )
        if created:
            script.sites.add(site)
            user, created = User.objects.get_or_create(username="admin")
            script.steps.add(ScriptStep.objects.create(
                    script=script,
                    message="Welcome to Ureport, where you can SPEAK UP and BE HEARD on what is happening in your community-it's FREE! "
                    ,
                    order=0,
                    rule=ScriptStep.WAIT_MOVEON,
                    start_offset=0,
                    giveup_offset=60,
                    ))
            poll = Poll.objects.create(name="youthgroup", user=user,
                                       question="First we need 2 know, are you part of any group? If yes, send us the NAME o+f the group. If no, text NO and just wait for the next set of instructions."
                                       , default_response='', type=Poll.TYPE_TEXT)
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
                    message="Ureport is a FREE SMS text message system that is sent to your phone.  Ureport is sponsored by UNICEF and other partners."
                    ,
                    order=2,
                    rule=ScriptStep.WAIT_MOVEON,
                    start_offset=60,
                    giveup_offset=60,
                    ))
            poll4 = Poll.objects.create(name='district', user=user, type=Poll.TYPE_TEXT,
                                        question="Its important to know which District you'll be reporting on so we can work together to try & resolve issues in your community!Reply ONLY with your district."
                                        , default_response="")
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
                    message="Ureport gives you a chance to speak out on issues in your community & share opinions with youth around Uganda!Best responses&results shared through the media!"
                    ,
                    order=4,
                    rule=ScriptStep.WAIT_MOVEON,
                    start_offset=60,
                    giveup_offset=60,
                    ))
            poll2 = Poll.objects.create(name="contactname", type=Poll.TYPE_TEXT, user=user,
                                        question="Best responses may be shared!Send us your name,or if you prefer a nickname so we can give u recognition for good replies by sharing them in the media!"
                                        , default_response="")
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
            poll5 = Poll.objects.create(name="contactage", type=Poll.TYPE_NUMERIC, question="What is your age?",
                                        default_response="", user=user)
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
            poll3 = Poll.objects.create(name="contactgender", type=Poll.TYPE_TEXT,
                                        question="Are you male or female?  Type F for female, and M for Male",
                                        default_response="", user=user)
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
                    regex=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['m', 'mal', 'male', 'ma'])),
                    rule_type=Rule.TYPE_REGEX,
                    rule_string=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['m', 'mal', 'male', 'ma'])))
            poll3.categories.create(name='female')
            poll3.categories.get(name='female').rules.create(
                    regex=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['f', 'fem', 'female', 'fe'])),
                    rule_type=Rule.TYPE_REGEX,
                    rule_string=(STARTSWITH_PATTERN_TEMPLATE % '|'.join(['f', 'fem', 'female', 'fe'])))

            poll9 = Poll.objects.create(name="contactvillage", type=Poll.TYPE_TEXT,
                                        question="Which village in the district do you currently live? Please respond ONLY with the name of your village."
                                        , default_response="", user=user)
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
                    message="CONGRATULATIONS!!! You are now a registered member of Ureport! With Ureport, you can make a real difference!  Speak Up and Be Heard! from UNICEF"
                    ,
                    order=9,
                    rule=ScriptStep.WAIT_MOVEON,
                    start_offset=60,
                    giveup_offset=0,
                    ))
            polls = [poll, poll2, poll3, poll4, poll5, poll9]
            for poll in polls:
                poll.sites.add(Site.objects.get_current())

post_syncdb.connect(create_auto_reg_script,
     dispatch_uid = "ureport.utils.create_auto_reg_script")