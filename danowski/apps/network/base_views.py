from django.http import JsonResponse
from django.views.generic import TemplateView

# JSON mixin and view borrowed from
# https://docs.djangoproject.com/en/1.8/topics/class-based-views/mixins/#jsonresponsemixin-example

class JSONResponseMixin(object):
    '''A mixin that can be used to render a JSON response.'''
    def render_to_json_response(self, context, **response_kwargs):
        '''Returns a JSON response, transforming 'context' to make the payload.'''
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        '''Returns an object that will be serialized as JSON by json.dumps().'''
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


class JSONView(JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

