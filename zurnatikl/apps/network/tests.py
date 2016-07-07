# -*- coding: utf-8 -*-
import codecs
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.http import StreamingHttpResponse
from mock import patch

from zurnatikl.apps.network.views import generate_network_graph
from zurnatikl.apps.network.base_views import CsvResponseMixin
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
        self.assertEqual(expected_node_count, len(graph.vs),
            '# of nodes should be total of locations, people, schools, and journal items')

        # inspect a couple of node attributes and edges
        p = people[0]
        pnode = graph.vs.find(name=p.network_id)
        self.assertEqual('Person', pnode['type'])
        self.assertEqual(unicode(p), pnode['label'])
        for k, v in p.network_attributes.iteritems():
            self.assertEqual(v, pnode[k])

        s = schools[0]
        snode = graph.vs.find(name=s.network_id)
        self.assertEqual('School', snode['type'])
        self.assertEqual(unicode(s), snode['label'])
        for k, v in s.network_attributes.iteritems():
            self.assertEqual(v, snode[k])

        item = items[0]
        itemnode = graph.vs.find(name=item.network_id)
        self.assertEqual('Item', itemnode['type'])
        self.assertEqual(unicode(item), itemnode['label'])
        for k, v in item.network_attributes.iteritems():
            self.assertEqual(v, itemnode[k])
        # check edges: item should be connected to creator and issue
        item_edges = graph.es.select(_target=itemnode.index)
        issue_node = graph.vs.find(name=item.issue.network_id)
        self.assert_(item_edges.find(_source=issue_node.index))
        creator_node = graph.vs.find(name=item.creators.first().network_id)
        self.assert_(item_edges.find(_source=creator_node.index))

        # check that unicode is preserved
        yugen = Journal.objects.filter(title__startswith='Y', title__endswith='gen').first()
        ynode = graph.vs.find(name=yugen.network_id)
        self.assertEqual(yugen.title.encode('utf-8'), ynode['label'],
            'unicode should be encoded for output by default')

    def test_ascii_output(self):
        graph = generate_network_graph(use_ascii=True)
        # check for journal title with unicode character Yūgen
        yugen = Journal.objects.filter(title__startswith='Y', title__endswith='gen').first()
        ynode = graph.vs.find(name=yugen.network_id)
        self.assertNotEqual(yugen.title, ynode['label'],
            'unicode should not be preserved when ascii is requested')
        self.assertEqual('Yugen', ynode['label'],
            'unicode characters should be converted to ascii equivalents when ascii is requested')

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

    def test_export_network_gml(self):
        response = self.client.get(reverse('network:data', kwargs={'fmt': 'gml'}))
        self.assertEqual('text/plain', response['Content-Type'],
            'mimetype should be set as text/plain for gml')
        disposition = response['Content-Disposition']
        self.assert_(disposition.endswith('.gml'),
            'content-disposition filename should end in .gml')
        self.assertContains(response, 'Creator "igraph version',
            msg_prefix='output should be in gml xml format')
        self.assertContains(response, 'Yugen',
            msg_prefix='gml should convert unicode to ascii')


class NetworkViewsTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_schools(self):
        # main schools network page just loads json & sigma js
        response = self.client.get(reverse('network:schools',
            kwargs={'slug': 'donald-allen'}))
        self.assertContains(response,
            reverse('network:schools-json', kwargs={'slug': 'donald-allen'}),
            msg_prefix='egograph page should load json for schools network')

    def test_schools_json(self):
        response = self.client.get(reverse('network:schools-json',
            kwargs={'slug': 'donald-allen'}))
        # basic sanity checking that this is json & looks as expected
        self.assertEqual(response['content-type'], 'application/json')
        self.assert_('edges' in response.content)
        self.assert_('nodes' in response.content)

    def test_egograph_export(self):
        # basic testing that the view is configured correctly

        # graphml
        response = self.client.get(reverse('network:schools-export',
            kwargs={'slug': 'donald-allen', 'fmt': 'graphml'}))
        self.assertEqual(response['content-type'], 'application/graphml+xml')
        self.assertContains(response, '<graphml')

        # gml format
        response = self.client.get(reverse('network:schools-export',
            kwargs={'slug': 'donald-allen', 'fmt': 'gml'}))
        self.assertEqual(response['content-type'], 'text/plain')
        self.assertContains(response, 'Creator "igraph version')


class CsvResponseMixinTest(TestCase):

    def test_get_data(self):
        csvresponse = CsvResponseMixin()
        testcsv = [
            ['title', 'note', 'etc'],
            ['title two', 'blah', 'foo']
        ]

        data = csvresponse.get_data(testcsv)
        # data should be an iterator; generator type test fails
        self.assert_(hasattr(data, 'next'),
            'csv data should be returned as a generator for streaming')
        data = ''.join(data)
        self.assert_(data.startswith(codecs.BOM_UTF8),
                    'data should start with UTF-8 byte order mark')
        # basic testing of that data is converted to csv
        for line in testcsv:
            self.assert_(','.join(line) in data)

        # with header row set
        csvresponse.header_row = ['title', 'author', 'date']
        data = ''.join(csvresponse.get_data(testcsv))
        self.assert_(','.join(csvresponse.header_row) in data,
            'csv output should include headings if set')

    def test_render_to_csv_response(self):
        csvresponse = CsvResponseMixin()
        with patch.object(csvresponse, 'get_data') as mockget_data:
            mockget_data.return_value = 'some test data'
            response = csvresponse.render_to_csv_response('')
            self.assert_(isinstance(response, StreamingHttpResponse))
            self.assertEqual(''.join(response.streaming_content),
                             mockget_data.return_value)
            self.assertEqual(response['content-type'],
                             'text/csv; charset=utf-8')
            self.assertEqual(response['content-disposition'],
                             'attachment; filename="data.csv"')

            # custom filename
            csvresponse.filename = 'my-data-file'
            response = csvresponse.render_to_csv_response('')
            self.assertEqual(response['content-disposition'],
                 'attachment; filename="my-data-file.csv"')