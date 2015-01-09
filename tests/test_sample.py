import unittest
from nose.exc import SkipTest


class TestMainCase(unittest.TestCase):
    def test_Ma(self):
        print "printing: Verify assert 1"
        self.assertTrue(1)

    def test_Mb(self):
        self.assertTrue(0, "raising: Some details")

    def test_Mc(self):
        print "printing: Verify assert 0"
        self.assertTrue(0, "raising: Some details")


class TestSecondCase(unittest.TestCase):
    def test_2a(self):
        print "printing: Verify assertTrue(1)"
        self.assertTrue(1)

    def test_2b(self):
        print "printing: Verify assertEqual(2, 0)"
        self.assertEqual(2, 0)


def test_a():
    """
    Test short description for test_a
    """
    print "printing: Verify assert 1"
    assert 1


def test_b():
    raise RuntimeError("raising: Some other details")


def test_c():
    raise SkipTest('raising: skipped')


def test_1():
    print("printing: Hello, world!")
    assert False


class TestFailedSetupCase(unittest.TestCase):
    def setUp(self):
        print("printing: Hello, world!")
        raise Exception("raising: bad")

    def test_whatever(self):
        """
        Verifying test short description and test error on setup fail
        """
        print "printing: Verify pass"
        pass
