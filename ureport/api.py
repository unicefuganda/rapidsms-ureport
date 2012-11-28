from tastypie.resources import ModelResource
from poll.models import Poll
from poll.models import ResponseCategory, Response
from rapidsms_httprouter.models import Message
from tastypie.authentication import ApiKeyAuthentication
from rapidsms.models import Connection,Contact
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS

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
    def dehydrate(self, bundle):
        bundle.data['responses_uri'] ="/api/v1/responses/?poll="+bundle.data['id']
        bundle.data['categories']=Poll.objects.get(pk=bundle.data['id']).categories.values_list('name',flat=True)
        return bundle.data
    class Meta:
        queryset = Poll.objects.exclude(start_date=None)
        excludes = ['response_type', 'type', 'default_response']
        resource_name = 'polls'
        allowed_methods = ['get']
        filtering = {
            'poll': ALL_WITH_RELATIONS
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






