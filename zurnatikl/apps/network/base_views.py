from datetime import datetime
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View
import logging
import os
import re
import tempfile
import time

from .utils import annotate_graph, node_link_data
from zurnatikl import __version__


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
    '''Convert a network graph into a JSON format appropriate for
    use with Sigma.js and serve it out as a JSON response.  Expects
    get_context_data to return the graph to be converted.'''

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
    export_format = 'graphml'     # also supports graphml
    filename = 'graph'         # default filename for download

    def render_to_network_export(self, context, **response_kwargs):
        graph = context
        # write out in requested format and return
        # NOTE: python-igraph is a wrapper around c libraries,
        # so it cannot operate on stringio buffers here; using
        # tempfile instead

        # NOTE: igraph outputs all node attributes for all nodes,
        # whether that node has a value for that attribute or note
        # - convert None to empty string before exporting
        for v in graph.vs:
            for data, val in v.attributes().iteritems():
                if val is None:
                    v[data] = ''

        buf = tempfile.TemporaryFile(suffix=self.export_format)
        if self.export_format == 'graphml':
            # cytoscape seems to look for name instead of label ...
            # in igraph, node name is internal network id
            graph.write_graphml(buf)
            buf.seek(0)
            content = buf.read()
            # NOTE: output includes empty data elements, e.g.
            #   <data key="v_genre"/>
            #   <data key="v_volume"/>
            #   <data key="v_publisher"/>
            # could use either regex or lxml.etree to find and remove them

            mimetype = 'application/graphml+xml'
            # NOTE: could not find an authoritative mimetype for graphml

        elif self.export_format == 'gml':
            graph.write_gml(buf, creator='/ zurnatikl %s %s' %
                            (__version__, datetime.now()))
            graph.write_gml(buf)
            mimetype = 'text/plain'
            # gml is an ascii format; unclear if it has a unique mimetype
            buf.seek(0)
            content = buf.read()
            # use regexes to remove empty attributes from the output
            content = re.sub(r'^\s+\w+\s""\s*$', '', content,
                             flags=re.MULTILINE)
            # consolidate multiple blank lines
            content = re.sub(r'\n+', "\n", content)

        response = HttpResponse(content, content_type=mimetype)
        # response['Content-Disposition'] = 'attachment; filename=%s.%s' %  \
        response['Content-Disposition'] = 'filename=%s.%s' %  \
            (self.filename, self.export_format)
        return response


class NetworkGraphExportView(NetworkGraphExportMixin, View):
    '''Re-usable view to export a graph as GraphML or GML.
    To support both formats, configure your url with a **fmt** parameter,
    along these lines::

       url(r'^data.(?P<fmt>graphml|gml)$', MyNetworkExport.as_view()),

    Defaults to graphml if format is not specified.  Set filename on
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
