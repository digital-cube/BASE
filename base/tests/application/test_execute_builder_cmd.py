import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from unittest import TestCase
import base.builder.project_maker


class TestExecute_builder_cmd(TestCase):

    def setUp(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def tearDown(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_builder(self, ss, se):
        # print('sys.argv', sys.argv)
        with self.assertRaises(SystemExit) as se:
            base.builder.project_maker.execute_builder_cmd()
        self.assertTrue(se, 2)


class TestExecute_builder_cmd_init_fail(TestCase):

    def setUp(self):
        sys.argv.append('init')
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def tearDown(self):
        sys.argv.remove('init')
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_init(self, ss ,se):
        # print('sys.argv', sys.argv)
        with self.assertRaises(SystemExit) as se:
            base.builder.project_maker.execute_builder_cmd()
        self.assertTrue(se, 2)


class TestExecute_builder_cmd_init_done(TestCase):

    def setUp(self):
        self.was_v = False
        self._dest = False
        self._desc = False
        self._port = False
        self._version = False
        self._prefix = False

        if '-v' in sys.argv:
            self.was_v = True
            sys.argv.remove('-v')

        sys.argv.append('init')
        sys.argv.append('luck')

    def tearDown(self):
        if self.was_v:
            sys.argv.append('-v')

        if self._dest:
            self._dest_tearDown()

        if self._desc:
            self._desc_tearDown()

        if self._port:
            self._port_tearDown()

        if self._version:
            self._version_tearDown()

        if self._prefix:
            self._prefix_tearDown()

        sys.argv.remove('init')
        sys.argv.remove('luck')

    def _dest_setUp(self):
        self._dest = True
        sys.argv.append('-D')
        sys.argv.append('new_dest')

    def _dest_tearDown(self):
        idx = sys.argv.index('-D')
        del sys.argv[idx+1]
        sys.argv.remove('-D')

    def _desc_setUp(self):
        self._desc = True
        sys.argv.append('-d')
        sys.argv.append('test description')

    def _desc_tearDown(self):
        idx = sys.argv.index('-d')
        del sys.argv[idx+1]
        sys.argv.remove('-d')

    def _port_setUp(self):
        self._port = True
        sys.argv.append('-p')
        sys.argv.append('9933')

    def _port_tearDown(self):
        idx = sys.argv.index('-p')
        del sys.argv[idx+1]
        sys.argv.remove('-p')

    def _version_setUp(self):
        self._version = True
        sys.argv.append('-v')
        sys.argv.append('1.0.0-test')

    def _version_tearDown(self):
        idx = sys.argv.index('-v')
        del sys.argv[idx+1]
        sys.argv.remove('-v')

    def _prefix_setUp(self):
        self._prefix = True
        sys.argv.append('-x')
        sys.argv.append('test')

    def _prefix_tearDown(self):
        idx = sys.argv.index('-x')
        del sys.argv[idx+1]
        sys.argv.remove('-x')

    @patch('base.builder.project_maker._build_project')
    @patch('base.builder.project_maker._build_database')
    def test_init(self, bp, bd):
        base.builder.project_maker.execute_builder_cmd()

    @patch('base.builder.project_maker._build_project')
    @patch('base.builder.project_maker._build_database')
    def test_init_with_destination(self, bp, bd):
        self._dest_setUp()
        base.builder.project_maker.execute_builder_cmd()

    @patch('base.builder.project_maker._build_project')
    @patch('base.builder.project_maker._build_database')
    def test_init_with_description(self, bp, bd):
        self._desc_setUp()
        base.builder.project_maker.execute_builder_cmd()

    @patch('base.builder.project_maker._build_project')
    @patch('base.builder.project_maker._build_database')
    def test_init_with_port(self, bp, bd):
        self._port_setUp()
        base.builder.project_maker.execute_builder_cmd()

    @patch('base.builder.project_maker._build_project')
    @patch('base.builder.project_maker._build_database')
    def test_init_with_version(self, bp, bd):
        self._version_setUp()
        base.builder.project_maker.execute_builder_cmd()

    @patch('base.builder.project_maker._build_project')
    @patch('base.builder.project_maker._build_database')
    def test_init_with_prefix(self, bp, bd):
        self._prefix_setUp()
        base.builder.project_maker.execute_builder_cmd()


class TestExecute_builder_cmd_db_init_fail(TestCase):

    def setUp(self):
        sys.argv.append('db_init')
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def tearDown(self):
        sys.argv.remove('db_init')
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_db_init(self, ss, se):
        with self.assertRaises(SystemExit) as se:
            base.builder.project_maker.execute_builder_cmd()
        self.assertTrue(se, 2)
