from poll.models import Poll
from poll.models import ResponseCategory, Response
from rapidsms_httprouter.models import Message
from rapidsms.models import Contact
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from django.db.models import Count


class MessageResource(ModelResource):
    class Meta:
        queryset = Message.objects.filter(direction="I")
        resource_name = 'messages'
        allowed_methods = ['get']
        #authentication = ApiKeyAuthentication()


class ResponseResource(ModelResource):
    #poll = fields.ForeignKey(PollResource, 'polls')
    def dehydrate(self, bundle):
        r=Response.objects.get(pk=bundle.data['id'])
        bundle.data['contact_id'] =r.contact.id
        bundle.data['message']=r.message.text
        bundle.data['categories']=r.categories.values_list('category__name',flat=True)
        return bundle.data
    class Meta:
        queryset = Response.objects.all()
        resource_name = 'responses'
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()


class PollResource(ModelResource):

    response_count = fields.IntegerField(readonly=True)

    def dehydrate(self, bundle):
        bundle.data['responses_uri'] = "/api/v1/responses/?poll=" + bundle.data['id']
        bundle.data['categories'] = Poll.objects.get(pk=bundle.data['id']).categories.values_list('name', flat=True)
        bundle.data['response_count'] = bundle.obj.response_count
        bundle.data['response_rate'] = (bundle.obj.response_count / float(bundle.obj.contacts.count())) * 100
        bundle.data['contacts_count'] = bundle.obj.contacts.count()
        return bundle.data

    class Meta:
        queryset = Poll.objects.exclude(start_date=None).annotate(response_count=Count('responses'))
        excludes = ['response_type', 'type', 'default_response']
        resource_name = 'polls'
        allowed_methods = ['get']
        filtering = {
            'poll': ALL_WITH_RELATIONS,
            'start_date': ['range', 'exact', 'lte', 'gte', 'lt', 'gt']
        }
        authentication = ApiKeyAuthentication()


class PollResponseResource(ModelResource):
    class Meta:
        queryset = Response.objects.all()
        resource_name = 'responsecategories'
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()


class PollResponseCategoryResource(ModelResource):
    class Meta:
        queryset = ResponseCategory.objects.all()
        resource_name = 'categories'
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()


class ContactResource(ModelResource):
    class Meta:
        queryset = Contact.objects.all()
        resource_name = 'contacts'
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
