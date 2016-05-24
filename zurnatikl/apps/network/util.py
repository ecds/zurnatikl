from collections import OrderedDict
import logging
from operator import add


# network utility methods borrowed from belfast code
# https://github.com/emory-libraries-ecds/belfast-group-site/blob/master/belfast/network/util.py

logger = logging.getLogger(__name__)


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


def annotate_graph(graph, fields):
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


def filter_graph(graph, min_degree):
    '''Filter a network graph by minimum degree.

    :param graph: :class:`networkx.graph.Graph` or subclass
    :param min_degree: minimum degree for nodes to be kept in the graph

    :returns: graph with only the nodes with degree higher or equal to
        the specified minimum, and all connecting edges among those nodes
    '''

    # filter a network graph by minimum degree
    nodes_to_keep = []
    degree = graph.degree()
    # iterate through the graph and identify nodes we want to keep
    for node in graph.nodes():
        if degree[node] >= min_degree:
            nodes_to_keep.append(node)

    # generate and return a subgraph with only those nodes and connecting edges
    return graph.subgraph(nodes_to_keep)