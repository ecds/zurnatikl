import networkx as nx
from networkx.readwrite import gexf
from StringIO import StringIO

from django.shortcuts import render
from django.http import HttpResponse

from danowski.apps.people.models import Person, School


def full_gexf(request):
    # generate a networkx and serialize as gexf
    graph = nx.MultiDiGraph()

    # add all the high-level objects to the network as nodes
    schools = School.objects.all()
    for s in schools:
        graph.add_node(s.network_id, **s.network_attributes)
    people = Person.objects.all()
    for p in people:
        graph.add_node(p.network_id, **p.network_attributes)

    # TODO: add nodes for locations, journals, issues, items
    # then add edges to connect everything

    # write out as GEXF and return
    buf = StringIO()
    gexf.write_gexf(graph, buf)
    response = HttpResponse(buf.getvalue(), content_type='application/gexf+xml')
    response['Content-Disposition'] = 'attachment; filename=danowski_data.gexf'
    return response





