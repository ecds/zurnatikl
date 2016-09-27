CHANGELOG
=========

Release 1.6 - Redesign and public release
-----------------------------------------

* As a user I want the network graphs to be generated more efficiently
  so I don’t have to wait while they are loaded and processed on my
  machine before they are displayed.
* As a user, I want to see an overlay of the Allen schools on the full
  contributor graph, so I can see how the network derived from his
  anthology relates to the network derived from the little magazine
  publication data.
* As a user, I want to be able to see that the Schooling Donald Allen
  site is part of a larger Digital Danowski initiative that encompasses
  multiple projects.
* As a user, I want to see labels for the network graph edges so I can
  more clearly understand how the network nodes are linked.
* As a user, I want to be able to see a contributor's "Name Used" for
  each item on his/her contributor page so I can determine which name(s)
  contributors were using for specific purposes.
* As a user, I want to be able to download bibliographic data and
  biographical data for people associated with the journals in CSV and
  network graph formats so I can conduct my own, independent research.
* As a user, I want to see a contributors' co-authors on his or her
  contributor page so that I get an accurate sense of their publication
  network.
* As a user, I want to filter journal contributors according to their
  roles so that I can explore the contributors that interest me.
* As a user, I want to see consistently designed content pages so that
  I have a consistent experience as I move through the site.
* As a user, on the journal contributor page, I want to see an indication
  of the number of items associated with each author & translator and
  the number of issues associated with each editor so that I can easily
  see how much data exists for every contributor.
* As a user, I want to be able to search the journal contributor names
  so that I can easily see if the database contains information about
  authors I care about.
* As a user, when I come to the site homepage, I want to see the main
  parts of the site and how to navigate to the parts that interest me.
* As a user, I want to be able to search the NNAP site from the navigation
  panel on any page so that I can explore specific terms in the project data.
* As a user, I want to see updated styling and navigation so that I have a
  consistent experience as I move through the site.
* As a user, I want to navigate forward and backward through journal issue
  pages using links at the top and bottom of each issue page so that I can
  navigate without having to scroll too much.
* As a user, I want to see breadcrumbs on the website so I can easily
  view and navigate the site hierarchy.
* As a user, I want to see a list of journals, a list of issues for each
  journal, and the detail pages for each journal issue in a style that matches
  the rest of the site so that I can easily explore the information that interests me.
* As a user, I want to see individual contributor pages with updated style
  and navigation so that I have a consistent experience as I move through the site.
* As a user, I want to see network graph pages with updated style and
  navigation so that I have a consistent experience as I move through the site.
* As a user, when I filter journal contributors by type of contribution I want
  the filtered page to show up in my browser history so I can easily return to
  the filtered list if I navigate away from the contributor page.
* As a user, I want to see contributors' alternate names on their individual
  pages so I can learn about other names that contributors use.
* As a user, if I toggle the menu bar closed, I want it to stay closed as I
  navigate around the site or if I reload pages so I can tailor my interaction
  with the site.
* As a user, I want to be able to see and search alternate names and aliases
  in the contributor list so that I can easily find data based on the names I know.
* As a user, when I filter the contributor network graph by school, I want to
  be able to see the other nodes so I can better understand how the schools
  relate to the entire graph.
* Updates to site text content

Upgrade to Django 1.9
^^^^^^^^^^^^^^^^^^^^^
* Tests were changed to call `save` on some test objects due to `new behavior for related objects <https://docs.djangoproject.com/en/1.9/releases/1.9/#bulk-behavior-of-add-method-of-related-managers>`_.
* Updated url files to make them plain lists. `django.conf.urls.patterns()` `will be removed in 1.10 <https://docs.djangoproject.com/en/1.9/ref/urls/>`_.
* `SortedDict` `was moved <https://docs.djangoproject.com/en/1.8/ref/utils/#django.utils.datastructures.SortedDict>`_ from `django.utils.datastructures.SortedDict` to `collections.OrderedDict`.
* Template settings were changed to `the new template api <https://docs.djangoproject.com/en/1.9/releases/1.8/#multiple-template-engines>`_.

There are still two depreciation warnings for 1.10. `SubfieldBase` will be removed in 1.10. It is called by `MultiSelectField` in `People.Models` and by `django_date_extensions` in `Journals.Models`.

Release 1.5.1
-------------

* Style tweaks: fix homepage image display for Firefox, adjust
  margins and heading for people page

Release 1.5 - Network graphs and site design
--------------------------------------------

* As a user, I want to see a network graph for individuals associated
  with the schools that Donald Allen categorized so I can visualize
  these relationships.
* As a user, I want to see a network graph of all journals, editors,
  authors, and translators so I can compare the relationships in our
  data set to the schools network graph.
* As a user, I want to see individuals and journals grouped by detected
  communities so I can compare those groups to the schools network graph.
* As a user, I want to see an indication of the type of node and lines
  in a graph, so that I can identify journals and types of contributors.
* As a user, I want a consistent way to access downloadable network
  files, so I can work with the content on my own.
* As a user, I want to view network graphs in fullscreen, so that I can
  interact with larger networks even on smaller screens.
* As a user, when I am browsing issues or contributor pages, I want to
  be able to navigate to other mentioned people, so that I can browse
  their connections.
* As a user, when browsing journal contributors, I want to filter by
  editor, author, or translator, so that I can narrow the list, or see
  specific types of contributors.
* As a user, when I come to the site homepage, I want to see the main
  parts of the site and how to navigate to the parts that interest me.
* As an admin, I want to upload images for use on the home page and
  secondary page banner so that I can manage the site image content.
* As a user, when I come to the home page of the site, I want to see a
  selection of images so that I can get a visual sense of materials
  related to the site.
* As a user, I want to see a consistent header and navigation so that I
  have a consistent experience as I move through the site.
* As an admin, I want to upload and associate a thumbnail with each
  journal so that I can give users a visual sense of each journal.
* As a user, I want to see images of journals, to have a sense of each
  journal's visual identity.

* GitHub repository and django project were renamed to use the codename
  **zurnatikl**.
* Switched from sigma.js to linkurious.js for network graph display.


Release 1.4 - Initial biography release
---------------------------------------

* As a user, I want to be able to see a list of authors, editors, and
  translators so I can know who published in or edited the journals
  represented.
* As a user, I want to see a list of titles published by a particular
  author or translated by a particular translator or a list of issues
  edited by a particular editor so I can know what they wrote and where
  it was published.
* As a user, I want to see a 1-degree ego visualization on an individual
  author’s, editor’s, or translator's biography page so I can know what
  people and journals they are connected to.
* As a user, I want to export a version of a person's ego graph to
  analyze in network analysis tools so I can better understand how they
  are connected to each other.
* As a user, when I add a journal or a person to the dataset I want the
  slug field to auto-populate so the slugs have a consistent logic to
  their creation.


Release 1.3 - Journal contents & admin improvements
---------------------------------------------------

Journal contents
^^^^^^^^^^^^^^^^
* As a user, I want to see a list of journals so I can find more information
  about their contents.
* As a user, I want to see a list of issues for a particular journal so
  I can understand the dates of publication and the number of issues
  published in order.
* As a user, I want to see the list of contents for a journal issue so
  I can know what was published in the issue.
* As a user, I want to be able to search within journal issues by
  author's name or a title keyword so I can find what I'm looking for.
* As a user, I want to be able to navigate from one issue of a journal
  to the previous or next issue so I can explore the contents of one journal.

Admin functionality
^^^^^^^^^^^^^^^^^^^
* As an admin user, I want all location fields to use an autocomplete rather
  than to display all the locations already in the database so the site
  loads more quickly.
* As an admin user, I want to be able to select multiple races for a
  person in the database so I can more accurately describe the people
  in our data.
* As an admin user, I want all person fields to use an autocomplete
  rather than to display all the person names already in the database so
  the site loads more quickly.
* As an admin, I want to be able to see what items/issue a location is
  attached to when editing that location so I can more effectively
  eliminate duplicates.
* As an admin user, I want to be able to add new persons as authors and
  new locations as places mentioned when creating a new item so I can
  work more efficiently.

Updates and bugfixes
^^^^^^^^^^^^^^^^^^^^
* Update to django 1.8
* bugfix: Searching on the issue portion of the database results in an
  error.


Release 1.2 - Initial data export
---------------------------------

* As a user, I want to export the data in a format that can be used in
  network analysis tools like Gephi or Cytoscape so that I can conduct
  independent analysis.
* As an admin, I want to be able to filter the issues and issue items by
  journal so I can more quickly see the items I'm interested in.
* As a user I want to be able to add multiple locations to a school so
  I can properly represent the information in our data.
* As a user, I want to use a horizontal filter for data fields where
  multiple entities can be selected so it's easier to see which entities
  have been selected.
* Upgraded to Django 1.7
* bugfix: admin searching on locations
* bugfix: links from location and person to items where they are mentioned

Release 1.1
-----------

* As a user of the database, I want to see more entries in the "Persons
  Mentioned" table so it's easier to see and select names of people
  mentioned.  (admin section to see objects associated with a particular person)
* As an admin, I want to be able to see which objects are associated
  with a particular location so I can make corrections to incorrect
  entries.  (admin section to see objects associated with a particular location)
* As an admin, I want to be able to see which objects are associated
  with a particular person so I can make corrections to incorrect
  entries.  (Updated UI style and added spacing for select options)
* bugfix: Pagination links are not visible


Release 1.0.1
-------------
* Added Natural Keys to assist with data loading

Release 1.0 - Data Entry
------------------------

* As an admin, I want to be able to create user accounts and give
  individual team members permission to edit the data so only permitted
  people can work on the data.
* As a team member, when I am editing a journal issue I want to be able
  to create a new location(s) or link to a pre-existing one(s) so I can
  capture place-based information about the issue.
* As a team member, when I'm editing a text I want to be able to add a
  new author without leaving the form so I can work efficiently.
* As a team member, when I'm editing a person I want to be able to
  create a new location or connect to a pre-existing one so I can
  capture place-based information about the author.
* As a team member, I want to add and edit people in order to describe
  them and link them to publications.
* As a team member, I want to add detailed information about schools of
  writing so I can see how these schools compare to publication
  networks.
* As a team member, I want add detailed information about addresses or
  locations so I can learn more about geographic distribution of the
  network.
* When a team member enters the admin framework they will be able to
  navigate the database with breadcrumb navigation so it's easier to get
  around the site.
* When a team member enters the admin framework they will see the models
  in the following order so they make hierarchical sense: Schools-
  People-Journals-Issues-Issue Items-Genres-Locations.
* Only admin users will be able to see the "Schools," "Journals," and
  "Genres" models so they can control changes to these models.
* As a team member, I want to add journals in order to describe them and
  their individual issues.
* As a team member, I want to add issues of a particular journal in order
  to describe them and their contents.
* When a team member goes to enter information into the database, they
  will choose from several different apps that encompass the models,
  namely Geo, People, and Journals.
* A user should be able to add all unicode characters to fields in the
  database so they can enter the text correctly.
* As a team member, I want to enter detailed information about each item
  in an issue so I can gather information about publication networks.
* When a team member is selecting a country for a location, they will
  see that the USA is the first choice in the list so they can save
  time.
* When a team member is looking at the Networks > Issue Items page, they
  will be able to see and sort by "Issue" so they can find what they're
  looking for more easily.
* When a team member chooses from any pre-populated list (like persons
  or issues), their choices are in alphabetical order (last-name first
  for persons) so it's easier to find the object they're looking for.
* When a user adds a "place mentioned" field in an "Issue Item", they
  can connect that place to the "locations" model of the database so the
  information becomes usable in multiple ways.
