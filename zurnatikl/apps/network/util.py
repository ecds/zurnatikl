from collections import OrderedDict
import logging
import networkx as nx
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
        vtx_data = vtx.attributes()
        vtx_data['id'] = vtx.index
        graph_data['nodes'].append(vtx_data)

    for edge in graph.es:
        graph_data['edges'].append({
            'id': edge.index,
            'source': edge.source,
            'target': edge.target
        })

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

    return graph


def nx_annotate_graph(graph, fields=[]):
    '''Annotate a :mod:`networkx` graph with network information.

    :param graph: :class:`networkx.graph.Graph` or subclass
    :param fields: list of fields to be added to the nodes in the graph;
        can include any of: degree, in_degree, out_degree,
        betweenness_centrality, eigenvector_centrality

    :returns: a graph with the requested annotations added to each node
        in the graph
    '''

    if 'degree' in fields:
        degree = graph.degree()
    # TODO: do we need to check that graph is directional for in/out degree?
    if 'in_degree' in fields and hasattr(graph, 'in_degree'):
        in_degree = graph.in_degree()
    if 'out_degree' in fields and hasattr(graph, 'out_degree'):
        out_degree = graph.out_degree()
    if 'betweenness_centrality' in fields:
        between = nx.algorithms.centrality.betweenness_centrality(graph)
    if 'eigenvector_centrality' in fields:
        use_g = graph
        if isinstance(graph, nx.MultiDiGraph):
            use_g = nx.DiGraph(graph)
        elif isinstance(graph, nx.MultiGraph):
            use_g = nx.Graph(graph)

        # NOTE: for a few graphs in production, eigenvector centrality fails:
        # "power iteration failed to converge in %d iterations"
        # (possibly an issue with something in the graph?)
        # Catch the error and don't include eigenvector centrality in
        # the graph
        try:
            eigenv = nx.algorithms.centrality.eigenvector_centrality(use_g)
        except nx.NetworkXError as err:
            logger.warn('Error generating eigenvector centrality: %s' % err)
            # remove from the list of fields so it will
            # be skipped below
            del fields[fields.index('eigenvector_centrality')]

    for node in graph.nodes():
        if 'degree' in fields:
            graph.node[node]['degree'] = degree[node]
        if 'in_degree' in fields and hasattr(graph, 'in_degree'):
            graph.node[node]['in_degree']= in_degree[node]
        if 'out_degree' in fields and hasattr(graph, 'out_degree'):
            graph.node[node]['out_degree']= out_degree[node]
        if 'betweenness_centrality' in fields:
            graph.node[node]['betweenness'] = between[node]
        if 'eigenvector_centrality' in fields:
            graph.node[node]['eigenvector_centrality'] = eigenv[node]

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