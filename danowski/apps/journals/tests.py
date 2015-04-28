from django.test import TestCase

from danowski.apps.geo.models import Location
from danowski.apps.journals.models import Journal, Issue, IssueItem, \
    PlaceName
from danowski.apps.people.models import School

class JournalTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_network_properties(self):
        # journal with a publisher
        beat = Journal.objects.get(title='Beatitude')
        # add a school to test edges
        beat.schools.add(School.objects.get(name__contains='Beat'))
        # one without
        floatingbear = Journal.objects.get(title__contains='Floating Bear')

        # network id
        self.assertEqual('journal:%d' % beat.id, beat.network_id)

        # network attributes
        net_attrs = beat.network_attributes
        self.assertEqual(unicode(beat), net_attrs['label'])
        self.assertEqual(beat.publisher, net_attrs['publisher'])
        # no publisher
        net_attrs = floatingbear.network_attributes
        self.assert_('publisher' not in net_attrs)

        # network edges
        # - no school = no edge
        self.assertFalse(floatingbear.has_network_edges,
            'journal not associated with a school should have no network edges')
        self.assertEqual([], floatingbear.network_edges)
        # school edge
        self.assertTrue(beat.has_network_edges,
            'journal not with a school should have network edges')
        edges = beat.network_edges
        self.assertEqual(beat.schools.count(), len(edges))
        # target element of the first edge should be the id of the first school
        self.assertEqual(beat.schools.first().network_id, edges[0][1])

class IssueTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_unicode(self):
        issue = Issue.objects.all().first()
        # no volume number
        self.assertEqual('%s Issue %s' % (issue.journal.title, issue.issue),
            unicode(issue))
        issue = Issue.objects.all()[1]
        # volume and issue
        self.assertEqual('%s Vol. %s Issue %s' % \
            (issue.journal.title, issue.volume, issue.issue),
            unicode(issue))

    def test_network_properties(self):
        issue = Issue.objects.all().first()

        # network id
        self.assertEqual('issue:%d' % issue.id, issue.network_id)

        # network attributes
        net_attrs = issue.network_attributes
        self.assertEqual(unicode(issue), net_attrs['label'])
        self.assertEqual(issue.issue, net_attrs['issue'])
        self.assertEqual(unicode(issue.publication_date), net_attrs['publication date'])
        # not present in data
        self.assert_('volume' not in net_attrs)

        # network edges
        # - editors, journal, publication addresses
        self.assertTrue(issue.has_network_edges),
        edges = issue.network_edges
        expected_edge_count = (1 if issue.journal else 0) \
            + issue.editors.count() + issue.contributing_editors.count() \
            + (1 if issue.publication_address else 0) \
            + (1 if issue.print_address else 0) \
            + issue.mailing_addresses.count()

        self.assertEqual(expected_edge_count, len(edges))
        # edge info: source, target, edge label (if any)
        edge_targets = [edge_info[1] for edge_info in edges]
        self.assert_(issue.journal.network_id in edge_targets)
        self.assert_(issue.publication_address.network_id in edge_targets)
        self.assert_(issue.editors.first().network_id in edge_targets)


class IssueItemTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_network_properties(self):
        item = IssueItem.objects.all().first()
        # add places mentioned for testing purposes
        pn = PlaceName(name='somewhere over the rainbow')
        pn.location = Location.objects.first()
        item.placename_set.add(pn)
        pn2 = PlaceName(name='the world\'s end')
        pn2.location = Location.objects.all()[1]
        item.placename_set.add(pn2)

        # network id
        self.assertEqual('issueitem:%d' % item.id, item.network_id)

        # network attributes
        attrs = item.network_attributes
        self.assertEqual(item.title, attrs['label'])
        self.assertEqual(item.anonymous, attrs['anonymous'])
        self.assertEqual(item.no_creator, attrs['no creator'])
        self.assertEqual(item.genre.first().name, attrs['genre'])
        self.assertEqual(unicode(item.issue), attrs['issue'])

        # network edges
        self.assertTrue(item.has_network_edges,
            'issue item should always have network edges (connected to issue, creator, etc)')
        edges = item.network_edges
        expected_edge_count = (1 if item.issue else 0) \
            + item.creators.count() + item.translator.count() \
            + item.persons_mentioned.count() + item.addresses.count() \
            + item.placename_set.count()
        self.assertEqual(expected_edge_count, len(edges))

        # edge info: source, target, edge label (if any)
        # create a dict of target network id and any edge properties
        edge_targets = {edge_info[1]: edge_info[2] if len(edge_info) == 3 else None
                        for edge_info in edges}
        self.assert_(item.issue.network_id in edge_targets)
        for c in item.creators.all():
            self.assert_(c.network_id in edge_targets)
            self.assertEqual({'label': 'creator'}, edge_targets[c.network_id],
                'issue edge to creator should be labeled')
        for t in item.translator.all():
            self.assert_(t.network_id in edge_targets)
            self.assertEqual({'label': 'translator'}, edge_targets[t.network_id],
                'issue edge to translator should be labeled')
        for p in item.persons_mentioned.all():
            self.assert_(p.network_id in edge_targets)
            self.assertEqual({'label': 'mentioned'}, edge_targets[t.network_id],
                'issue edge to person mentioned should be labeled')
        for a in item.addresses.all():
            self.assert_(a.network_id in edge_targets)
        for pn in item.placename_set.all():
            self.assert_(pn.location.network_id in edge_targets)
            self.assertEqual({'label': 'mentioned'}, edge_targets[pn.location.network_id],
                'issue edge to placename should be labeled')
