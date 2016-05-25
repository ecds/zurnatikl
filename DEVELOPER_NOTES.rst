The following instructions can be ignored when deploying to a staging
or production environment, but may be helpful to a developer working
on the project or running automated tests.

Data Entry Group and DB migrations
----------------------------------

When creating a new database from scratch (or building the test db),
the data migration that creates the Data Entry Group will fail when
running all migrations.  If it fails, you should see a warning with the
loaddata command to use, or you can undo and re-run the migration::

  python manage.py migrate danowski_admin 0001
  python manage.py migrate danowski_admin 0002


Tests, database migrations, & fixtures
--------------------------------------

:mod:`zurnatikl` uses Django migrations to manage the database.
Any initial data should be explicitly included as test
fixtures where they are required.

sigma.js / linkurious
---------------------

Note that the version of sigma.js used in this project is the
version distributed by linkurious.js.

Linkurious documentation: https://github.com/Linkurious/linkurious.js/wiki

