from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
import logging
from lxml import etree
from networkx.readwrite import gexf, graphml, json_graph
import os
from StringIO import StringIO
import time

from .util import annotate_graph, node_link_data


logger = logging.getLogger(__name__)


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


class SigmajsJSONView(JSONView):
    '''Convert an nx network graph into a JSON format appropriate for
    use with Sigma.js and serve it out as a JSON response.  Expects
    get_context_data to return the nx graph to be converted.'''

    # by default, annotate all graphs with degree
    annotate_fields = ['degree']

    def get_context_data(self, **kwargs):
        graph = super(SigmajsJSONView, self).get_context_data(**kwargs)

        if self.annotate_fields:
            start = time.time()
            graph = annotate_graph(graph, self.annotate_fields)
            logger.debug('Annotated graph with %s in %.2f sec' %
                         (', '.join(self.annotate_fields),
                          time.time() - start))
        start = time.time()
        data = node_link_data(graph)
        logger.debug('Generated json in %.2f sec' %
                     (time.time() - start))

        return data


class NetworkGraphExportMixin(object):
    export_format = 'gexf'     # also supports graphml
    filename = 'graph'         # default filename for download

    gexf_labels_xslt = os.path.join(settings.BASE_DIR, 'zurnatikl',
                'apps', 'network', 'gexf_labels.xslt')
    gexf_labels_transform = etree.XSLT(etree.parse(gexf_labels_xslt))

    def render_to_network_export(self, context, **response_kwargs):
        graph = context
        # write out in requested format and return
        buf = StringIO()
        if self.export_format == 'gexf':
            gexf.write_gexf(graph, buf)
            # networkx gexf output does not include edge labels in a format
            # that Gephi can import them.
            # Use a simple XSLT to adjust the xml to allow the Gephi import
            # to get the edge labels.

            # NOTE: should be possible for lxml to read directly from the buffer,
            # e.g. etree.parse(buf), but that errors
            doc = etree.XML(buf.getvalue())
            content = self.gexf_labels_transform(doc)
            mimetype = 'application/gexf+xml'
        elif self.export_format == 'graphml':
            # cytoscape seems to look for name instead of label, so copy it in
            for n in graph.nodes():
                graph.node[n]['name'] = graph.node[n]['label']
            graphml.write_graphml(graph, buf)
            content = buf.getvalue()
            mimetype = 'application/graphml+xml'   # maybe? not sure authoritative mimetype

        response = HttpResponse(content, content_type=mimetype)
        response['Content-Disposition'] = 'attachment; filename=%s.%s' %  \
            (self.filename, self.export_format)
        return response


class NetworkGraphExportView(NetworkGraphExportMixin, View):
    '''Re-usable view to export a networkx graph as GEXF or GraphML.
    To support both formats, configure your url with a **fmt** parameter,
    along these lines::

       url(r'^data.(?P<fmt>gexf|graphml)$', MyNetworkExport.as_view()),

    Defaults to GEXF if format is not specified.  Set filename on
    extended class to customize default filename for download.
    '''

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_network_export(context, **response_kwargs)

    # based on django's TemplateView
    def get(self, request, *args, **kwargs):
        # set format if present in kwargs
        if 'fmt' in kwargs:
            self.export_format = kwargs['fmt']
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
