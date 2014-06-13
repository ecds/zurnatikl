The following instructions can be ignored when deploying to a staging
or production environment, but may be helpful to a developer working
on the project or running automated tests.


Tests, South, & fixtures
------------------------

:mod:`danwoski` uses :mod:`south` to manage and db models.
Any initial data should be explicitly included as test 
fixtures where they are required.

