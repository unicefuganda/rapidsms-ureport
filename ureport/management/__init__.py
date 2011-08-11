from django.db.models.signals import post_syncdb
from script.models import ScriptStep

def update_auto_reg_polls(app, created_models, verbosity, **kwargs):
    """
    Update the autoreg steps order 1 and 8
    refer to ureport.management.commands.create_autoreg_script
    """
    #update poll for scriptstep with order 1
    step_1=ScriptStep.objects.get(order=1)
    step_1.poll.question="First we need 2 know, are you part of a group? If yes, send us the NAME of the group. If no, text NO and just wait for the next set of instructions."
    step_1.poll.save()
    step_1.save()
    #update poll for scriptstep with order 8
    step_8=ScriptStep.objects.get(order=8)
    step_8.poll.question="Which village in the district  do you currently live? Please respond ONLY with the name of your village."
    step_8.poll.save()
    step_8.save()

post_syncdb.connect(update_auto_reg_polls,sender = ScriptStep)
