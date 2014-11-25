import StringIO
import re
import codecs
import inspect
import os
import traceback
from collections import defaultdict

from jinja2 import Environment
from jinja2 import FileSystemLoader
from nose.exc import SkipTest
from nose.plugins import Plugin
import sys

__version__ = '0.1.0'

TEST_ID = re.compile(r'^(.*?)(\(.*\))$')


def id_split(idval):
    m = TEST_ID.match(idval)
    if m:
        name, fargs = m.groups()
        head, tail = name.rsplit(".", 1)
        return [head, tail+fargs]
    else:
        return idval.rsplit(".", 1)


def nice_classname(obj):
    """Returns a nice name for class object or class instance.

        >>> nice_classname(Exception()) # doctest: +ELLIPSIS
        '...Exception'
        >>> nice_classname(Exception) # doctest: +ELLIPSIS
        '...Exception'

    """
    if inspect.isclass(obj):
        cls_name = obj.__name__
    else:
        cls_name = obj.__class__.__name__
    mod = inspect.getmodule(obj)
    if mod:
        name = mod.__name__
        # jython
        if name.startswith('org.python.core.'):
            name = name[len('org.python.core.'):]
        return "%s.%s" % (name, cls_name)
    else:
        return cls_name


def exc_message(exc_info):
    """Return the exception's message."""
    exc = exc_info[1]
    if exc is None:
        # str exception
        result = exc_info[0]
    else:
        try:
            result = str(exc)
        except UnicodeEncodeError:
            try:
                result = unicode(exc)  # flake8: noqa
            except UnicodeError:
                # Fallback to args as neither str nor
                # unicode(Exception(u'\xe6')) work in Python < 2.6
                result = exc.args[0]
    return result


class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()

stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


class Group(object):
    def __init__(self):
        self.stats = {'errors': 0, 'failures': 0, 'passes': 0, 'skipped': 0}
        self.tests = []


class HtmlReport(Plugin):
    """
    Output test results as pretty html.
    """

    name = 'html'
    score = 2000
    encoding = 'UTF-8'
    report_file = None

    stdout0 = None
    stderr0 = None

    # def __init__(self, verbosity=1):
    #     super(HtmlReport, self).__init__()
    #     self.stdout0 = None
    #     self.stderr0 = None
    #     self.verbosity = verbosity

    def startTest(self, test):
        super(HtmlReport, self).startTest(self, test)
        # just one buffer for both stdout and stderr
        self.outputBuffer = StringIO.StringIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        super(HtmlReport, self).stopTest(test)
        self.complete_output()

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option(
            '--html-report', action='store',
            dest='html_file', metavar="FILE",
            default=env.get('NOSE_HTML_FILE', 'nosetests.html'),
            help="Path to html file to store the report in. "
                 "Default is nosetests.html in the working directory "
                 "[NOSE_HTML_FILE]")
        parser.add_option(
            '--html-report-template', action='store',
            dest='html_template', metavar="FILE",
            default=env.get('NOSE_HTML_TEMPLATE_FILE',
                            os.path.join(os.path.dirname(__file__), "templates", "report.html")),
            help="Path to html template file in with jinja2 format."
                 "Default is report.html in the lib sources"
                 "[NOSE_HTML_TEMPLATE_FILE]")

    def configure(self, options, config):
        """Configures the xunit plugin."""
        Plugin.configure(self, options, config)
        self.config = config
        if self.enabled:
            self.jinja = Environment(
                loader=FileSystemLoader(os.path.dirname(options.html_template)),
                trim_blocks=True,
                lstrip_blocks=True
            )
            self.stats = {'errors': 0, 'failures': 0, 'passes': 0, 'skipped': 0}
            self.report_data = defaultdict(Group)
            self.report_file = codecs.open(options.html_file, 'w', self.encoding, 'replace')
            self.report_template_filename = options.html_template

    def report(self, stream):
        """Writes an Xunit-formatted XML file

        The file includes a report of test errors and failures.

        """
        self.stats['total'] = sum(self.stats.values())
        for group in self.report_data.values():
            group.stats['total'] = sum(group.stats.values())
        self.report_file.write(self.jinja.get_template(os.path.basename(self.report_template_filename)).render(
            report=self.report_data,
            stats=self.stats,
        ))
        self.report_file.close()
        if self.config.verbosity > 1:
            stream.writeln("-" * 70)
            stream.writeln("HTML: %s" % self.report_file.name)

    def addSuccess(self, test):
        name = id_split(test.id())
        group = self.report_data[name[0]]
        self.stats['passes'] += 1
        group.stats['passes'] += 1
        group.tests.append({
            'name': name[-1],
            'failed': False,
            'output': self._format_output(self.complete_output()),
        })

    def addError(self, test, err, capt=None):
        """Add error output to Xunit report.
        """
        exc_type, exc_val, tb = err
        tb = ''.join(traceback.format_exception(
            exc_type,
            exc_val if isinstance(exc_val, exc_type) else exc_type(exc_val),
            tb
        ))
        name = id_split(test.id())
        group = self.report_data[name[0]]
        if issubclass(err[0], SkipTest):
            type = 'skipped'
            self.stats['skipped'] += 1
            group.stats['skipped'] += 1
        else:
            type = 'error'
            self.stats['errors'] += 1
            group.stats['errors'] += 1
        group.tests.append({
            'name': name[-1],
            'failed': True,
            'type': type,
            'errtype': nice_classname(err[0]),
            'message': exc_message(err),
            'tb': tb,
            'output': self._format_output(self.complete_output()),
        })

    def addFailure(self, test, err, capt=None):
        """Add failure output to Xunit report.
        """
        exc_type, exc_val, tb = err
        tb = ''.join(traceback.format_exception(
            exc_type,
            exc_val if isinstance(exc_val, exc_type) else exc_type(exc_val),
            tb
        ))
        name = id_split(test.id())
        group = self.report_data[name[0]]
        self.stats['failures'] += 1
        group.stats['failures'] += 1
        group.tests.append({
            'name': name[-1],
            'failed': True,
            'errtype': nice_classname(err[0]),
            'message': exc_message(err),
            'tb': tb,
            'output': self._format_output(self.complete_output()),
        })

    def _format_output(self, o):
        if isinstance(o, str):
            return o.decode('latin-1')
        else:
            return o