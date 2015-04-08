import networkx as nx
from networkx.readwrite import gexf
from StringIO import StringIO

from django.http import HttpResponse

from danowski.apps.geo.models import Location
from danowski.apps.journals.models import Journal, Issue, IssueItem
from danowski.apps.people.models import Person, School


def full_gexf(request):
    # generate a networkx and serialize as gexf
    graph = nx.MultiDiGraph()

    # add all the high-level objects to the network as nodes

    # dictionary of objects to be added to the network as nodes
    # label for type of node -> Model class for the data
    # models should have network_id and network_attributes properties
    node_classes = {
        'School': School,
        'Person': Person,
        'Location': Location,
        'Journal': Journal,
        'Issue': Issue,
        'IssueItem': IssueItem,
    }
    nodes = {}

    # TODO: add logging here so it is easier to tell what is going on


    for node_type, model in node_classes.iteritems():
        # find all objects
        nodes[node_type] = model.objects.all()
        # add to the network with attributes and the specified type
        graph.add_nodes_from(
            [(n.network_id, n.network_attributes) for n in nodes[node_type]],
            type=node_type)

    # then add edges to connect everything
    for node_group in nodes.itervalues():
        # NOTE: should be possible to add a list of edges all at once,
        # but will require testing to see if that is more efficient
        for node in node_group:
            if node.has_network_edges:
                graph.add_edges_from(node.network_edges)

    # write out as GEXF and return
    buf = StringIO()
    gexf.write_gexf(graph, buf)
    response = HttpResponse(buf.getvalue(), content_type='application/gexf+xml')
    response['Content-Disposition'] = 'attachment; filename=danowski_data.gexf'
    return response





