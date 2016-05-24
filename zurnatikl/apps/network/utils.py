# utility methods for generating network graphs from application data

import logging
import time
import unicodedata

logger = logging.getLogger(__name__)

def to_ascii(d):
    # convert unicode to ascii, converting accented characters to
    # non-accented equivalents where possible
    return {k: unicodedata.normalize('NFD', v).encode('ascii', 'ignore') if isinstance(v, unicode) else v
                 for k, v in d.iteritems()}

def encode_unicode(data):
    return {k: v.encode("utf-8") if isinstance(v, unicode) else v
            for k, v in data.iteritems()}

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
