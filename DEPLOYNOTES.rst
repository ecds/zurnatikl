.. _DEPLOYNOTES:

Installation
============

Software dependencies
---------------------

We recommend the use of `pip <http://pip.openplans.org/>`_ and `virtualenv
<http://virtualenv.openplans.org/>`_ for environment and dependency management
in this and other Python projects. If you don't have them installed we
recommend ``sudo easy_install pip`` and then ``sudo pip install virtualenv``.

Bootstrapping a development environment
---------------------------------------

* Copy ``zurnatikl/localsettings.py.dist`` to ``zurnatikl/localsettings.py``
  and configure any local settings: **DATABASES**,  **SECRET_KEY**,
  customize **LOGGING**, etc.
* Create a new virtualenv and activate it.
* Install fabric: ``pip install fabric``
* Install igraph dependencies before pip install: on Mac OSX, use
  ``brew install homebrew/science/igraph``; on Debian/Ubuntu try
  ``apt-get install libigraph0``.
* Use fabric to run a local build, which will install python dependencies in
  your virtualenv, run unit tests, and build sphinx documentation: ``fab build``

After configuring your instance, run database  migrations:

    python manage.py migrate

Deploy to QA and Production should be done using ``fab deploy``.

Configure the environment
~~~~~~~~~~~~~~~~~~~~~~~~~

*Alternate, manual setup instructions*

When first installing this project, you'll need to create a virtual environment
for it. The environment is just a directory. You can store it anywhere you
like; in this documentation it'll live right next to the source. For instance,
if the source is in ``/home/httpd/zurnatikl/src``, consider creating an
environment in ``/home/httpd/zurnatikl/env``. To create such an environment, su
into apache's user and::

  $ virtualenv --no-site-packages /home/httpd/zurnatikl/env

This creates a new virtual environment in that directory. Source the activation
file to invoke the virtual environment (requires that you use the bash shell)::

  $ . /home/httpd/zurnatikl/env/bin/activate

Once the environment has been activated inside a shell, Python programs
spawned from that shell will read their environment only from this
directory, not from the system-wide site packages. Installations will
correspondingly be installed into this environment.

.. Note::
  Installation instructions and upgrade notes below assume that
  you are already in an activated shell.

Install python dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

zurnatikl depends on several python libraries. The installation is mostly
automated, and will print status messages as packages are installed. If there
are any errors, pip should announce them very loudly.

.. Note::

  On Mac OS X, you may want to run::

   brew install homebrew/science/igraph

  before installing **python-igraph** via pip.


To install python dependencies, cd into the repository checkout and::

  $ pip install -r requirements.txt

If you are a developer or are installing to a continuous ingration server
where you plan to run unit tests, code coverage reports, or build sphinx
documentation, you probably will also want to::

  $ pip install -r requirements/dev.txt

After this step, your virtual environment should contain all of the
needed dependencies.

Install the application
-----------------------

Apache
~~~~~~

After installing dependencies, copy and edit the wsgi and apache
configuration files in src/apache inside the source code checkout. Both may
require some tweaking for paths and other system details.

Configuration
~~~~~~~~~~~~~

Configure application settings by copying ``localsettings.py.dist`` to
``localsettings.py`` and editing for local settings (database etc.).

After configuring all settings, initialize the db with all needed
tables and initial data using::

  $ python manage.py migrate

.. Note::
  If the database is not set to use the ``UTF8`` character set by default you will have to create the database
  with the followng command::

    CREATE DATABASE <DBNAME> DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;


Upgrade Notes
=============

1.5
---

* Run migrations for changes and updates to the database structure::

      python manage.py migrate

* Configure **MEDIA_ROOT** in ``localsettings.py`` and configure
  apache to serve out media content.

* If variant sizes of user uploaded images do not generate, or need to
  be regenerated, run the following::

      python manage.py rendervariations journals.Journal.image [--replace]
      python manage.py rendervariations content.Image.image [--replace]

1.4
---

* Run migrations for changes and updates to the database structure::

      python manage.py migrate

1.3
---

* Run migrations for changes and updates to the database structure::

      python manage.py migrate

1.2
---

* This update includes an upgrade from Django 1.6 to 1.7, which replaces
  south migrations with Django migrations.  Existing installations with
  data should fake the new initial migrations::

      python manage.py migrate --fake

* Remove :mod:`south` from your python virtualenv:

      pip uninstall south
