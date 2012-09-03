#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from script.models import ScriptStep
from django.contrib.auth.decorators import login_required
from generic.views import generic
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from rapidsms_xforms.models import  XFormField
from ussd.models import StubScreen
from poll.models import Poll,Category,Rule,Translation,Response
from poll.forms import CategoryForm,RuleForm2
from rapidsms.models import Contact
from ureport.forms import NewPollForm
from django.conf import settings
from ureport.forms import AssignToPollForm,SearchResponsesForm, AssignResponseGroupForm, ReplyTextForm,DeleteSelectedForm
from django.contrib.sites.models import Site
from ureport.tasks import start_poll
from ureport.utils import  get_polls , get_script_polls
from generic.sorters import SimpleSorter
from ureport.views.utils.paginator import ureport_paginate
from ureport.tasks import reprocess_responses

@login_required
def view_poll(request,pk):
    poll=Poll.objects.get(pk=pk)
    category=None
    if request.GET.get('poll'):
        if request.GET.get('start'):
            start_poll.delay(poll)
            res=""" <a href="?stop=True&poll=True" data-remote=true  id="poll_action" class="btn">Close Poll</a> """
            return HttpResponse(res)
        if request.GET.get('stop'):
            poll.end()
            res=""" <a href="?reopen=True&poll=True" data-remote=true id="poll_action" class="btn">Reopen Poll</a> """
            return HttpResponse(res)
        if request.GET.get("reopen"):
            poll.end_date=None
            poll.save()
            res="""<a href="?stop=True&poll=True" data-remote=true  id="poll_action" class="btn">Close Poll</a>  """
            return HttpResponse(res)
    xf=XFormField.objects.get(name='latest_poll')
    response=StubScreen.objects.get(slug='question_response')
    template='ureport/polls/view_poll.html'
    categories=poll.categories.all()
    category_form=CategoryForm()
    rule_form=RuleForm2()
    if request.method == "POST":
        if request.GET.get('edit'):
            if request.POST.get('poll[default_response]'):
                poll.default_response=request.POST['poll[default_response]']
                poll.save()
            if request.POST.get('poll[question]'):
                poll.default_response=request.POST['poll[question]']
                poll.save()

        if request.GET.get("ussd",None):
            question=request.POST.get("question")
            response=request.POST.get("response")
            xf.question=question
            xf.save()
            response.text=response
            response.save()
        if request.GET.get("category",None):
            if request.GET.get('pk'):
                category=Category.objects.get(pk=int(pk))
            else:
                category=Category()
                category.poll=poll
            category_form=CategoryForm(request.POST,instance=category)
            if category_form.is_valid():
                template="ureport/polls/rules.html"
                category=category_form.save()
                request.session['category'] =category
            else:
                template="ureport/polls/category.html"

        if request.GET.get("rules",None):
            rule=Rule()
            rule.category=request.session['category']
            rule_form=RuleForm2(request.POST,instance=rule)
            if rule_form.is_valid:
                rule_form.save()
            else:
                template="ureport/polls/rules.html"





    return render_to_response(template, {
        'poll': poll,
        'xf':xf,
        'response':response,
        'categories': categories,
        'category_form':category_form,
        'rule_form':rule_form,
        'category':category ,
        }, context_instance=RequestContext(request))


@permission_required('poll.can_poll')
def new_poll(req):
    if req.method == 'POST':
        form = NewPollForm(req.POST)
        form.updateTypes()
        if form.is_valid():
            # create our XForm
            question = form.cleaned_data['question']
            default_response = form.cleaned_data['default_response']
            districts = form.cleaned_data['districts']
            if hasattr(Contact, 'groups'):
                groups = form.cleaned_data['groups']

            if len(districts):
                contacts = Contact.objects.filter(reporting_location__in=districts).filter(groups__in=groups).distinct()
            else:
                contacts = Contact.objects.filter(groups__in=groups).distinct()

            name = form.cleaned_data['name']
            p_type = form.cleaned_data['type']
            response_type = form.cleaned_data['response_type']
            if not form.cleaned_data['default_response_luo'] == ''\
            and not form.cleaned_data['default_response'] == '':
                (translation, created) =\
                Translation.objects.get_or_create(language='ach',
                    field=form.cleaned_data['default_response'],
                    value=form.cleaned_data['default_response_luo'])

            if not form.cleaned_data['question_luo'] == '':
                (translation, created) =\
                Translation.objects.get_or_create(language='ach',
                    field=form.cleaned_data['question'],
                    value=form.cleaned_data['question_luo'])

            poll_type = (Poll.TYPE_TEXT if p_type
            == NewPollForm.TYPE_YES_NO else p_type)

            poll = Poll.create_with_bulk(\
                name,
                poll_type,
                question,
                default_response,
                contacts,
                req.user)

            if p_type == NewPollForm.TYPE_YES_NO:
                poll.add_yesno_categories()

            if settings.SITE_ID:
                poll.sites.add(Site.objects.get_current())

            return redirect(reverse('ureport.views.view_poll', args=[poll.pk]))

    else:
        form = NewPollForm()
        form.updateTypes()

    return render_to_response('ureport/new_poll.html', {'form': form},
        context_instance=RequestContext(req))


@cache_control(no_cache=True, max_age=0)
def poll_summary(request):
    script_polls =\
    ScriptStep.objects.exclude(poll=None).values_list('poll',
        flat=True)
    polls =\
    Poll.objects.exclude(pk__in=script_polls).exclude(start_date=None).order_by('-start_date')
    return render_to_response('/ureport/poll_summary.html', {'polls'
                                                             : polls, 'poll': polls[0]},
        context_instance=RequestContext(request))


@login_required
def view_responses(req, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)

    script_polls =\
    ScriptStep.objects.exclude(poll=None).values_list('poll',
        flat=True)
    response_rates = {}
    if poll.pk in script_polls:
        responses = poll.responses.order_by('-date')
    else:
        if hasattr(Contact, 'groups'):
            responses =\
            poll.responses.filter(contact__groups__in=req.user.groups.all()).distinct()
        else:
            responses = poll.responses.all()
        responses = responses.order_by('-date')

        for group in req.user.groups.all():
            try:
                contact_count =\
                poll.contacts.filter(groups__in=[group]).distinct().count()
                response_count =\
                poll.responses.filter(contact__groups__in=[group]).distinct().count()
                response_rates[str(group.name)] = [contact_count]
                response_rates[str(group.name)].append(response_count)
                response_rates[str(group.name)].append(response_count
                                                       * 100.0 / contact_count)
            except ZeroDivisionError:
                response_rates.pop(group.name)
    typedef = Poll.TYPE_CHOICES[poll.type]
    print typedef
    columns = [('Sender', False, 'sender', None)]
    for (column, style_class, sortable, db_field, sorter) in\
    typedef['report_columns']:
        columns.append((column, sortable, db_field, sorter))

    return generic(
        req,
        model=Response,
        response_rates=response_rates,
        queryset=responses,
        objects_per_page=25,
        selectable=True,
        partial_base='ureport/partials/polls/poll_partial_base.html',
        base_template='ureport/responses_base.html',
        paginator_template='ureport/partials/pagination.html',
        row_base=typedef['view_template'],
        action_forms=[AssignToPollForm, AssignResponseGroupForm, ReplyTextForm,
                      DeleteSelectedForm],
        filter_forms=[SearchResponsesForm],
        columns=columns,
        partial_row='ureport/partials/polls/response_row.html',
    )


@login_required
def edit_category(request,pk):
    category=Category.objects.get(pk=int(pk))
    category_form=CategoryForm(instance=category)
    title="Editing "+category.name
    return render_to_response("ureport/polls/category.html",{'category':category,'category_form':category_form,'edit':True,"title":title},context_instance=RequestContext(request))

@login_required
def view_rules(request,pk):
    category=Category.objects.get(pk=int(pk))
    rules=category.rules.all()
    rule=Rule()
    rule.category=category
    rule_form=RuleForm2(instance=rule)
    return render_to_response("ureport/polls/rules.html",{'rules':rules,'rule_form':rule_form,'category':category,"edit":True},context_instance=RequestContext(request))


def create_rule(request,pk):
    rule_form=RuleForm2(request.POST or None)
    category=Category.objects.get(pk=int(pk))

    if rule_form.is_valid():
        rule=rule_form.save(commit=False)
        rule.category=category
        rule.save()
        reprocess_responses.delay(category.poll)
        if rule.rule == 1:
            r="Contains all of"
        else:
            r="Contains one of"
        res="<td >"+r+"</td><td>"+rule.rule_string+"</td>"

        return HttpResponse(res)
    return HttpResponse("<td colspan='2'>Please enter all the fields</td>")



@login_required
def poll_dashboard(request):
    columns=[('Name', True, 'name', SimpleSorter()),
        ('Question', True, 'question', SimpleSorter(),),
        ('Start Date', True, 'start_date', SimpleSorter(),),
        ('# Participants', False, 'participants', None,),
        ('Visuals', False, 'visuals', None,),
    ]
    return generic(request,
        model=Poll,
        queryset=get_polls,
        results_title='Polls',
        objects_per_page=10,
        partial_row='ureport/partials/dashboard/poll_row.html',
        partial_header='ureport/partials/dashboard/partial_header_dashboard.html',
        base_template='ureport/dashboard.html',
        paginator_template='ureport/partials/new_pagination.html',
        paginator_func=ureport_paginate,
        selectable=False,
        sort_column='start_date'
    )

@login_required
def ureport_polls(request):
    columns=[('Name', True, 'name', SimpleSorter()),
        ('Question', True, 'question', SimpleSorter(),),
        ('Start Date', True, 'start_date', SimpleSorter(),),
        ('Closing Date', True, 'end_date', SimpleSorter()),
        ('', False, '', None)]
    return generic(request,
        model=Poll,
        queryset=get_polls,
        objects_per_page=10,
        selectable=False,
        partial_row='ureport/partials/polls/poll_admin_row.html',
        base_template='ureport/poll_admin_base.html',
        paginator_template='ureport/partials/new_pagination.html',
        results_title='Polls',
        paginator_func=ureport_paginate,
        sort_column='start_date',
        sort_ascending=False,
    )


@login_required
def script_polls(request):
    columns=[('Name', True, 'name', SimpleSorter()),
        ('Question', True, 'question', SimpleSorter(),),
        ('Start Date', True, 'start_date', SimpleSorter(),),
        ('Closing Date', True, 'end_date', SimpleSorter()),
        ('', False, '', None)]
    return generic(request,
            model=Poll,
            queryset=get_script_polls,
            objects_per_page=10,
            selectable=False,
            partial_row='ureport/partials/polls/poll_admin_row.html',
            base_template='ureport/poll_admin_base.html',
            paginator_template='ureport/partials/new_pagination.html',
            paginator_func=ureport_paginate,
            results_title='Polls',
            sort_column='start_date',
            auto_reg=True,
            sort_ascending=False,
            columns=columns)
