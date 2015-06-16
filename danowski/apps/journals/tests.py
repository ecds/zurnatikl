from django.test import TestCase
from django.core.urlresolvers import reverse

from danowski.apps.geo.models import Location
from danowski.apps.journals.models import Journal, Issue, Item, \
    PlaceName
from danowski.apps.journals.templatetags.journal_extras import \
    readable_list, all_except
from danowski.apps.people.models import School, Person

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
        self.assertEqual('%s Volume %s, Issue %s' % \
            (issue.journal.title, issue.volume, issue.issue),
            unicode(issue))

    def test_label(self):
        issue = Issue.objects.all().first()
        # no volume number
        self.assertEqual('Issue %s' % (issue.issue),
            issue.label)
        issue = Issue.objects.all()[1]
        # volume and issue
        self.assertEqual('Volume %s, Issue %s' % \
            (issue.volume, issue.issue),
            issue.label)

    def test_next_previous(self):
        # create journal + issues to test next/previous issue
        journal = Journal(title='A Journal')
        journal.save()
        issue1 = Issue(issue=1, sort_order=1, journal=journal)
        issue1.save()
        issue2 = Issue(issue=2, sort_order=2, journal=journal)
        issue2.save()
        issue3 = Issue(issue=3, sort_order=3, journal=journal)
        issue3.save()

        self.assertEqual(None, issue1.previous_issue)
        self.assertEqual(issue2, issue1.next_issue)
        self.assertEqual(issue1, issue2.previous_issue)
        self.assertEqual(issue3, issue2.next_issue)
        self.assertEqual(issue2, issue3.previous_issue)
        self.assertEqual(None, issue3.next_issue)

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


class ItemTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_network_properties(self):
        item = Item.objects.all().first()
        # add places mentioned for testing purposes
        pn = PlaceName(name='somewhere over the rainbow')
        pn.location = Location.objects.first()
        item.placename_set.add(pn)
        pn2 = PlaceName(name='the world\'s end')
        pn2.location = Location.objects.all()[1]
        item.placename_set.add(pn2)
        # placenames can apparently have an empty location?
        # placename without location can't contribute a network edge
        pn3 = PlaceName(name='Xanadu')
        item.placename_set.add(pn3)

        # network id
        self.assertEqual('item:%d' % item.id, item.network_id)

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
            + item.creators.count() + item.translators.count() \
            + item.persons_mentioned.count() + item.addresses.count() \
            + item.placename_set.filter(location__isnull=False).count()
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
        for t in item.translators.all():
            self.assert_(t.network_id in edge_targets)
            self.assertEqual({'label': 'translator'}, edge_targets[t.network_id],
                'issue edge to translator should be labeled')
        for p in item.persons_mentioned.all():
            self.assert_(p.network_id in edge_targets)
            self.assertEqual({'label': 'mentioned'}, edge_targets[t.network_id],
                'issue edge to person mentioned should be labeled')
        for a in item.addresses.all():
            self.assert_(a.network_id in edge_targets)
        for pn in item.placename_set.filter(location__isnull=False).all():
            self.assert_(pn.location.network_id in edge_targets)
            self.assertEqual({'label': 'mentioned'}, edge_targets[pn.location.network_id],
                'issue edge to placename should be labeled')


class JournalViewsTestCase(TestCase):
    fixtures = ['test_network.json']

    def test_list_journals(self):
        response = self.client.get(reverse('journals:list'))
        journals = Journal.objects.all()
        for j in journals:
            self.assertContains(response, j.title)
            # publishers removed from journal list display
            # if j.publisher:
            #     self.assertContains(response, j.publisher)

    def test_journal_detail(self):
        intrepid = Journal.objects.get(title='Intrepid')

        response = self.client.get(reverse('journals:journal', kwargs={'slug': intrepid.slug}))

        self.assertContains(response, intrepid.title,
            msg_prefix='Journal detail page should include journal title')
        for issue in intrepid.issue_set.all():
            self.assertContains(response, issue.label,
                msg_prefix='Journal detail page should include issue label')
            self.assertContains(response, issue.publication_date,
                msg_prefix='Journal detail page should include issue publication date')
            for ed in issue.editors.all():
                self.assertContains(response, '%s %s' % (ed.first_name, ed.last_name),
                    msg_prefix='Journal detail page should list editor')

        # check 404
        response = self.client.get(reverse('journals:journal', kwargs={'slug': 'bogus'}))
        self.assertEqual(404, response.status_code)

    def test_issue_detail(self):
        intrepid = Journal.objects.get(title='Intrepid')
        issue = intrepid.issue_set.all().first()

        response = self.client.get(reverse('journals:issue',
            kwargs={'journal_slug': intrepid.slug, 'id': issue.id}))

        self.assertContains(response, issue.journal.title,
            msg_prefix='issue detail should include journal title')
        self.assertContains(response,
            reverse('journals:journal', kwargs={'slug': issue.journal.slug}),
            msg_prefix='issue detail should link to journal')
        self.assertContains(response, 'Issue %s' % issue.issue,
            msg_prefix='issue detail should include issue number')
        self.assertContains(response, '(%s)' % issue.publication_date,
            msg_prefix='issue detail should include issue publication date')
        ed = issue.editors.all().first()
        self.assertContains(response, '<h3>%s %s, editor</h3>' % (ed.first_name, ed.last_name),
            html=True, msg_prefix='issue detail should list editor')
        self.assertContains(response, 'Published at %s' % issue.publication_address.display_label,
            msg_prefix='issue detail should include publication address')
        self.assertNotContains(response, 'Printed at',
            msg_prefix='issue detail should not include printed address if not set')
        self.assertNotContains(response, 'Price per issue',
            msg_prefix='issue detail should not include price if not set')

        # item display
        for item in issue.item_set.all():
            self.assertContains(response, item.start_page,
                msg_prefix='issue item listing should display start page')
            self.assertContains(response, item.end_page,
                msg_prefix='issue item listing should display end page')
            self.assertContains(response, item.title,
                msg_prefix='issue item listing should display title')
            auth = item.creators.all().first()
            self.assertContains(response, '%s %s' % (auth.first_name, auth.last_name),
                msg_prefix='issue item listing should display creator name')

        # add test issue with full details to check display
        new_issue = Issue(volume='2', issue='5', season='Summer',
            publication_date='1968-06-01', journal=intrepid, price=0.50)
        new_issue.save()
        people = Person.objects.all()
        new_issue.editors.add(people[0], people[1], people[2])
        new_issue.contributing_editors.add(people[3], people[4])
        locations = Location.objects.all()
        new_issue.publication_address = locations[0]
        new_issue.print_address = locations[1]
        new_issue.save()

        response = self.client.get(reverse('journals:issue',
            kwargs={'journal_slug': intrepid.slug, 'id': new_issue.id}))

        self.assertContains(response, 'Volume %s' % new_issue.volume,
            msg_prefix='issue detail should include volume # when present')
        self.assertContains(response, 'Published at %s' % new_issue.publication_address.display_label,
            msg_prefix='issue detail should include publication address')
        self.assertContains(response, 'Printed at %s' % new_issue.print_address.display_label,
            msg_prefix='issue detail should include print address')
        self.assertContains(response, 'Price per issue: $%s' % new_issue.price,
            msg_prefix='issue detail should include price if set')

        # list of names display
        eds = new_issue.editors.all()
        self.assertContains(response,
            '<h3>%s %s, %s %s and %s %s, editors</h3>' % \
             (eds[0].first_name, eds[0].last_name,
             eds[1].first_name, eds[1].last_name,
             eds[2].first_name, eds[2].last_name),
             html=True,
             msg_prefix='multiple editor names should be listed')
        # NOTE: using html test so whitespace differences will be ignored

        c_eds = new_issue.contributing_editors.all()
        self.assertContains(response,
            '<h3>%s %s and %s %s, contributing editors</h3>' % \
             (c_eds[0].first_name, c_eds[0].last_name,
             c_eds[1].first_name, c_eds[1].last_name),
             html=True,
             msg_prefix='multiple contributing editor names should be listed')

        # check 404 - valid issue id with wrong journal slug should 404
        response = self.client.get(reverse('journals:issue',
            kwargs={'journal_slug': 'beatitude', 'id': issue.id}))
        self.assertEqual(404, response.status_code)

    def test_search(self):
        search_url = reverse('journals:search')

        # no search term
        response = self.client.get(search_url)
        self.assertContains(response, 'Please enter one or more search terms')
        self.assertNotContains(response, 'No items found')

        # search term with no matches
        response = self.client.get(search_url, {'keyword': 'not in the data'})
        self.assertNotContains(response, 'Please enter one or more search terms')
        self.assertContains(response, 'No items found')

        # search with one match - search on both title and author
        item = Item.objects.get(title='[Maple Bridge Night Mooring]')
        response = self.client.get(search_url, {'keyword': 'maple bridge zhang'})

        # should display item title, author (if any), journal, issue,
        # with link to issue detail view
        self.assertContains(response, item.title,
            msg_prefix='search results should display item title')
        self.assertContains(response, item.issue.journal.title,
            msg_prefix='search results should display journal item belongs to')
        self.assertContains(response, item.issue.label,
            msg_prefix='search results should display issue the item belongs to')
        self.assertContains(response,
            reverse('journals:issue',
                kwargs={'journal_slug': item.issue.journal.slug,
                        'id': item.issue.id}),
            msg_prefix='search results should link to issue the item belongs to')


## test custom template tags

class ReadableListTestCase(TestCase):

    def test_readable_list(self):
        # empty
        self.assertEqual('', readable_list([]))

        # one item
        self.assertEqual('one', readable_list(['one']))
        # attribute specified
        self.assertEqual('1', readable_list([Item(title='1')], 'title'))

        # two items
        self.assertEqual('one and two', readable_list(['one', 'two']))
        # attribute specified
        self.assertEqual('1 and 2', readable_list(
            [Item(title='1'), Item(title='2')], 'title'))

        # three or more items
        self.assertEqual('one, two, and three',
            readable_list(['one', 'two', 'three']))
        # attribute specified
        self.assertEqual('1, 2, and 3', readable_list(
            [Item(title='1'), Item(title='2'), Item(title='3')], 'title'))

        self.assertEqual('one, two, three, and four',
            readable_list(['one', 'two', 'three', 'four']))
        # attribute specified
        self.assertEqual('1, 2, 3, and 4', readable_list(
            [Item(title='1'), Item(title='2'), Item(title='3'),
             Item(title='4')], 'title'))

    def test_error_handling(self):
        self.assertEqual(None, readable_list(1))


class AllExceptTestCase(TestCase):

    def test_all_except(self):
        self.assertEqual([], all_except([], 'foo'))
        self.assertEqual([], all_except(['foo'], 'foo'))
        self.assertEqual(['bar', 'baz'], all_except(['foo', 'bar', 'baz'], 'foo'))
        self.assertEqual(['foo', 'baz'], all_except(['foo', 'bar', 'baz'], 'bar'))
        self.assertEqual(['foo', 'bar'], all_except(['foo', 'bar', 'baz'], 'baz'))
        # technically, can be used on a string too
        self.assertEqual(['o', 's', 'e', 's', 'e'], all_except('nonsense', 'n'))

        self.assertEqual(None, all_except(1, 'one'))