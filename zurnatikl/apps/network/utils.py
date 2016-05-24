# utility methods for generating network graphs from application data
from collections import OrderedDict
import logging
from operator import add
import unicodedata


logger = logging.getLogger(__name__)


def to_ascii(data):
    # convert unicode to ascii, converting accented characters to
    # non-accented equivalents where possible
    return {k: unicodedata.normalize('NFD', v).encode('ascii', 'ignore')
            if isinstance(v, unicode) else v
            for k, v in data.iteritems()}


def encode_unicode(data):
    # encode as utf-8 (e.g., for output via igraph write methods)
    return {k: v.encode("utf-8") if isinstance(v, unicode) else v
            for k, v in data.iteritems()}

# NOTE: it might be cleaner to refactor into graph subclass with these methods


def egograph(graph, vertex):  # support configurable radius?
    '''Filter a graph around a specified vertex to generate an egograph.
    Currently only supports a radius of one.'''

    # identify the set of vertices we want to keep: the central
    # vertex and all its immediate neighbors
    neighbors = graph.neighbors(vertex)
    vertices = set([vertex]) | set(neighbors)

    # NOTE: should be possible to support radius > 1 by iteratively
    # fnding and adding neighbors of neighbors

    # filter the graph to just the requested vertices
    return graph.subgraph(vertices)


def annotate_graph(graph, fields):
    '''Annotate graph vertices with calculated values like degree for
    use in export and display.
    '''
    in_degree = out_degree = None
    if 'in_degree' in fields:
        in_degree = graph.indegree()
        graph.vs['in_degree'] = in_degree
    if 'out_degree' in fields:
        out_degree = graph.outdegree()
        graph.vs['out_degree'] = out_degree
    if 'degree' in fields:
        # igraph doesn't expose a method for degree directly
        # so calculate by adding in & out degrees
        if in_degree is None:
            in_degree = graph.indegree()
        if out_degree is None:
            out_degree = graph.outdegree()
        degree = map(add, in_degree, out_degree)
        # add degree to as node data
        graph.vs['degree'] = degree

    # NOTE: previous networkx annotate_graph method
    # also supported betweenness_centrality and eigenvector_centrality,
    # but those do not seem to be used anywhere currently

    return graph


def node_link_data(graph):
    '''Generate node and edge dictionary to be output as json
    for use with sigma.js'''
    graph_data = OrderedDict([
        ('directed', graph.is_directed()),
        ('multigraph', any(graph.is_multiple())),
        ('nodes', []),
        ('edges', [])
    ])
    for vtx in graph.vs:
        # include any vertex attributes present in the graph
        vtx_data = vtx.attributes()
        vtx_data['id'] = vtx.index
        graph_data['nodes'].append(vtx_data)

    for edge in graph.es:
        # include edge attributes, like labels and size
        edge_data = edge.attributes()
        edge_data.update({
            'id': edge.index,
            'source': edge.source,
            'target': edge.target
        })
        graph_data['edges'].append(edge_data)

    return graph_data
