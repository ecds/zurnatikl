# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase

from zurnatikl.apps.network.views import generate_network_graph
from zurnatikl.apps.geo.models import Location
from zurnatikl.apps.journals.models import Journal, Issue, Item
from zurnatikl.apps.people.models import Person, School

class GenerateNetworkTest(TestCase):
    fixtures = ['test_network.json']

    def test_generate_network(self):
        graph = generate_network_graph()
        locations = Location.objects.all()
        people = Person.objects.all()
        schools = School.objects.all()
        journals = Journal.objects.all()
        issues = Issue.objects.all()
        items = Item.objects.all()
        expected_node_count = locations.count() + people.count() + schools.count() \
            + journals.count() + issues.count() + items.count()
        self.assertEqual(expected_node_count, graph.number_of_nodes(),
            '# of nodes should be total of locations, people, schools, and journal items')

        # inspect a couple of node attributes and edges
        p = people[0]
        pnode = graph.node[p.network_id]
        self.assertEqual('Person', pnode['type'])
        self.assertEqual(unicode(p), pnode['label'])
        for k, v in p.network_attributes.iteritems():
            self.assertEqual(v, pnode[k])

        s = schools[0]
        snode = graph.node[s.network_id]
        self.assertEqual('School', snode['type'])
        self.assertEqual(unicode(s), snode['label'])
        for k, v in s.network_attributes.iteritems():
            self.assertEqual(v, snode[k])

        item = items[0]
        itemnode = graph.node[item.network_id]
        self.assertEqual('Item', itemnode['type'])
        self.assertEqual(unicode(item), itemnode['label'])
        for k, v in item.network_attributes.iteritems():
            self.assertEqual(v, itemnode[k])
        # check edges: item should be connected to creator and issue
        item_edges = graph.edge[item.network_id]
        self.assert_(item.issue.network_id in item_edges)
        self.assert_(item.creators.first().network_id in item_edges)

        # check that unicode is preserved
        yugen = Journal.objects.filter(title__startswith='Y', title__endswith='gen').first()
        ynode = graph.node[yugen.network_id]
        self.assertEqual(yugen.title, ynode['label'],
            'unicode should be preserved by default')

    def test_ascii_output(self):
        graph = generate_network_graph(use_ascii=True)
        # check for journal title with unicode character Yūgen
        yugen = Journal.objects.filter(title__startswith='Y', title__endswith='gen').first()
        ynode = graph.node[yugen.network_id]
        self.assertNotEqual(yugen.title, ynode['label'],
            'unicode should not be preserved when ascii is requested')
        self.assertEqual('Yugen', ynode['label'],
            'unicode characters should be converted to ascii equivalents when ascii is requested')

    def test_export_network_gexf(self):
        response = self.client.get(reverse('network:data', kwargs={'fmt': 'gexf'}))
        self.assertEqual('application/gexf+xml', response['Content-Type'],
            'mimetype should be set as gexf')
        disposition = response['Content-Disposition']
        self.assert_('attachment' in disposition,
            'content-disposition should specify attachment')
        self.assert_('filename' in disposition,
            'content-disposition should specify filename')
        self.assert_(disposition.endswith('.gexf'),
            'content-disposition filename should end in .gexf')
        self.assertContains(response, '<gexf',
            msg_prefix='output should be in gexf xml format')
        self.assertContains(response, 'Yugen',
            msg_prefix='gexf output should convert unicode to ascii')
        self.assertContains(response, ' label="mentioned">',
            msg_prefix='gexf output should include edge labels')


    def test_export_network_graphml(self):
        response = self.client.get(reverse('network:data', kwargs={'fmt': 'graphml'}))
        self.assertEqual('application/graphml+xml', response['Content-Type'],
            'mimetype should be set as graphml')
        disposition = response['Content-Disposition']
        self.assert_(disposition.endswith('.graphml'),
            'content-disposition filename should end in .graphml')
        self.assertContains(response, '<graphml',
            msg_prefix='output should be in graphml xml format')
        self.assertNotContains(response, 'Yugen',
            msg_prefix='graphml should not convert unicode to ascii')
        # NOTE: could also test labels getting copied to names
