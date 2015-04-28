import logging
from lxml import etree
import networkx as nx
from networkx.readwrite import gexf, graphml
import os
from StringIO import StringIO
import time
import unicodedata

from django.conf import settings
from django.http import HttpResponse

from danowski.apps.geo.models import Location
from danowski.apps.journals.models import Journal, Issue, IssueItem
from danowski.apps.people.models import Person, School


logger = logging.getLogger(__name__)


def to_ascii(d):
    # convert unicode to ascii, converting accented characters to
    # non-accented equivalents where possible
    return {k: unicodedata.normalize('NFD', v).encode('ascii', 'ignore') if isinstance(v, unicode) else v
                 for k, v in d.iteritems()}

# NOTE: it might be cleaner to refactor into graph class with these methods

def add_nodes_to_graph(qs, graph, node_type, use_ascii=False, chunksize=1000):
    # some models have large number of items, handle them in chunks
    for i in xrange(0, qs.count(), chunksize):
        chunk = qs[i:i + chunksize]
        # add to the network with attributes and the specified type
        start = time.time()
        graph.add_nodes_from(
            [(n.network_id,
              to_ascii(n.network_attributes) if use_ascii else n.network_attributes)
             for n in chunk],
            type=node_type)
        logger.debug('Added %d %s nodes in %.2f sec' % \
            (len(chunk), node_type, time.time() - start))

def add_edges_to_graph(qs, graph, node_type):
    # NOTE: should be possible to add a list of edges all at once,
    # but will require testing to see if that is more efficient
    logger.debug('adding %s edges' % node_type)
    start = time.time()
    for node in qs:
        if node.has_network_edges:
            graph.add_edges_from(node.network_edges)

    logger.debug('Added edges for %d nodes in %.2f sec' % \
        (qs.count(), time.time() - start))


def generate_network_graph(use_ascii=False):
    '''Generate a :class:`networkx.MultiGraph` from the connections among
    schools, people, locations, journals, issues, and items.
    Optionally convert unicode to ascii, if needed by the export tool.
    '''

    # generate a networkx graph for serialization
    # TODO: probably need to add caching on this graph
    graph = nx.MultiGraph()
    start = time.time()

    # add all the high-level objects to the network as nodes
    schools = School.objects.all()
    add_nodes_to_graph(schools, graph, 'School', use_ascii)
    people = Person.objects.all().prefetch_related('schools', 'dwelling')
    add_nodes_to_graph(people, graph, 'Person', use_ascii)
    locations = Location.objects.all().prefetch_related('placename_set')
    add_nodes_to_graph(locations, graph, 'Location', use_ascii)
    journals = Journal.objects.all()
    add_nodes_to_graph(journals, graph, 'Journal', use_ascii)
    issues = Issue.objects.all().prefetch_related('editors',
        'contributing_editors', 'publication_address', 'print_address',
        'mailing_addresses')
    add_nodes_to_graph(issues, graph, 'Issue', use_ascii)
    items = IssueItem.objects.all().prefetch_related('issue', 'creators',
        'translator', 'persons_mentioned', 'addresses', 'genre')
    add_nodes_to_graph(items, graph, 'Issue Item', use_ascii)

    # then add edges to connect everything

    add_edges_to_graph(schools, graph, 'School')
    add_edges_to_graph(people, graph, 'Person')
    # locations do not have any outbound edges
    add_edges_to_graph(journals, graph, 'Journal')
    add_edges_to_graph(issues, graph, 'Issue')
    add_edges_to_graph(items, graph, 'Issue Item')

    logger.debug('Generated full graph in %.2f sec' % (time.time() - start))

    return graph


def export_network(request, fmt):
    '''Export the full network graph for use in external network analysis
    software.'''
    # NOTE: GEXF supports unicode, but Gephi seems to have an import bug
    # with unicode, so disabling it now
    use_ascii = (fmt == 'gexf')
    graph = generate_network_graph(use_ascii=use_ascii)
    # write out in requested format and return
    buf = StringIO()
    if fmt == 'gexf':
        gexf.write_gexf(graph, buf)
        # networkx gexf output does not include edge labels in a format
        # that Gephi can import them.
        # Use a simple XSLT to adjust the xml to allow the Gephi import
        # to get the edge labels.

        # NOTE: should be possible for lxml to read directly from the buffer,
        # e.g. etree.parse(buf), but that errors
        doc = etree.XML(buf.getvalue())
        gexf_labels_xslt = os.path.join(settings.BASE_DIR, 'danowski',
            'apps', 'network', 'gexf_labels.xslt')
        # with open(gexf_labels_xslt) as f:
        gexf_labels_transform = etree.XSLT(etree.parse(gexf_labels_xslt))
        content = gexf_labels_transform(doc)
        mimetype = 'application/gexf+xml'
    elif fmt == 'graphml':
        # cytoscape seems to look for name instead of label, so copy it in
        for n in graph.nodes():
            graph.node[n]['name'] = graph.node[n]['label']
        graphml.write_graphml(graph, buf)
        content = buf.getvalue()
        mimetype = 'application/graphml+xml'   # maybe? not sure authoritative mimetype
    response = HttpResponse(content, content_type=mimetype)
    response['Content-Disposition'] = 'attachment; filename=danowski_data.%s' % fmt
    return response





