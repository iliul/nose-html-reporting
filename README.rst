===============================
nose-html-reporting
===============================

Nose plugin that generates a nice html test report with ability of using template based on jinja2 templates from any folder.

* Free software: BSD license

Installation
============

::

    pip install nose-html-reporting

Usage
=====

  --with-html           Enable plugin HtmlOutput:  Output test results as
                        pretty html.  [NOSE_WITH_HTML]
  --html-file=FILE      Path to html file to store the report in. Default is
                        nosetests.html in the working directory
  --html-report-template=FILE      Path to jinja2 file to get the report template from. Default is
                        templates/report.html from the package working directory

Development
===========

To run the all tests run::

    tox

Example
=======
To execute tests::

    nosetests tests/test_sample.py --with-html --html-report=nose_report2_test.html --html-report-template=src/nose_htmlreport/templates/report2.jinja2

.. image:: https://raw.githubusercontent.com/lysenkoivan/nose-html-reporting/master/docs/sample.png
