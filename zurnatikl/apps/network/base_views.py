import codecs
from cStringIO import StringIO
from datetime import datetime
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.generic import TemplateView, View
import logging
import itertools
import os
import re
import tempfile
import time
import unicodecsv

from .utils import annotate_graph, node_link_data, to_ascii, encode_unicode
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
    get_context_data to return the graph to be converted.

    Graph layout, community detection, and layout caching can be
    configured by extending classes.
    '''

    #: annotate nodes with graph data; by default, annotate with degree
    annotate_fields = ['degree']

    #: layout algorithm to use
    # layout = 'fruchterman_reingold'
    layout = 'auto'
    # auto layout chooses layout based on graph size
    # > 100 uses Kamada-Kawai force-directed
    # > 1000 uses Fruchterman-Reingold
    # graphs larger than that use drl

    #: enable layout caching
    cache_layout = False

    #: enable community detection
    community_detection = False

    def layout_cache_key(self):
        return '%s-layout' % self.request.path

    def get_graph_layout(self, graph):
        # calculate a graph layout
        # NOTE: full contributor network layout takes ~4s to calculate
        # the layout should probably be cached, for that graph at least

        # if layout caching is configured, check for a cached layout
        if self.cache_layout:
            # for now, set cache to never timeout; may need to be
            # more configurable later on
            layout = cache.get(self.layout_cache_key(), None)
            # if layout was cached, return it immediately
            if layout is not None:
                logger.debug('Using cached graph layout for %s',
                             self.request.path)
                return layout

        # generate layout if caching is not turned on or not in cache
        start = time.time()
        layout = graph.layout(self.layout)
        logger.debug('Calculated graph layout in %.2f sec',
                     time.time() - start)

        # if caching is configured, store the generated layout
        if self.cache_layout:
            cache.set(self.layout_cache_key(), layout)

        return layout

    def get_context_data(self, **kwargs):
        graph = super(SigmajsJSONView, self).get_context_data(**kwargs)

        if self.annotate_fields:
            start = time.time()
            graph = annotate_graph(graph, self.annotate_fields)
            logger.debug('Annotated graph with %s in %.2f sec' %
                         (', '.join(self.annotate_fields),
                          time.time() - start))

        # layout the graph
        layout = self.get_graph_layout(graph)

        # community detetion, if requested
        cluster = None
        if self.community_detection:
            start = time.time()
            # fastgreedy only works on undirected
            # dend = graph.community_fastgreedy(weights='weight')
            # cluster = graph.community_infomap(edge_weights='weight')

            # leading eigenvector community looks nice
            # cluster = graph.community_leading_eigenvector(weights='weight')
            # NOTE: generates warning, developed for undirected graphs

            # this one looks pretty good too
            cluster = graph.community_walktrap(weights='weight').as_clustering()

            logger.debug('Community detection in %.2f sec', time.time() - start)

        start = time.time()
        data = node_link_data(graph, layout, cluster)
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
        # - convert to unicode or ascii based on format
        for vtx in graph.vs:
            vtx_attr = vtx.attributes()
            if self.export_format == 'graphml':
                vtx_attr = encode_unicode(vtx_attr)
            elif self.export_format == 'gml':
                vtx_attr = to_ascii(vtx_attr)
            for key, val in vtx_attr.iteritems():
                if val is None:
                    vtx[key] = ''
                else:
                    vtx[key] = val

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


class EchoBuffer(object):
    """An object that implements just the write method of the file-like
    interface.  Used for streaming CSV output, taken from
    https://docs.djangoproject.com/en/1.9/howto/outputting-csv/#streaming-large-csv-files
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class CsvResponseMixin(object):
    '''A mixin that can be used to render CSV output.  Override filename
    to customize default download name.  If header_row is defined, it will
    be output first.  To take advantage of streaming downloads,
    get_context_data should return a generator of rows to be output
    as CSV.  Uses unicodecsv for output and sets content as UTF-8.'''
    filename = 'data'
    header_row = []

    def render_to_csv_response(self, context, **response_kwargs):
        '''Returns a CSV response, with context output as CSV data.'''
        response = StreamingHttpResponse(
            self.get_data(context),
            content_type="text/csv; charset=utf-8",
            # content_type="text/plain; charset=utf-8",
            **response_kwargs
        )

        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % \
            self.filename
        return response

    def get_data(self, context):
        '''Returns a generator of CSV data rows.'''
        writer = unicodecsv.writer(EchoBuffer())
        # add byte-order mark so programs like Excel know to open as UTF-8
        header = [codecs.BOM_UTF8]
        if self.header_row:
            header.append(writer.writerow(self.header_row))
        return itertools.chain(
            header,
            (writer.writerow(row) for row in context)
        )


class CsvView(CsvResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_csv_response(context, **response_kwargs)
