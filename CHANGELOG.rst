CHANGELOG
=========

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
