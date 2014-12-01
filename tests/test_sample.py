import unittest
from nose.exc import SkipTest


class TestMainCase(unittest.TestCase):
    def test_Ma(self):
        print "printing: Verify assert 1"
        self.assertTrue(1)

    def test_Mb(self):
        self.assertTrue(0, "raising: Some details")


class TestSecondCase(unittest.TestCase):
    def test_2a(self):
        print "printing: Verify assertTrue(1)"
        self.assertTrue(1)

    def test_2b(self):
        print "printing: Verify assertTrue(1)"
        self.assertTrue(1)


def test_a():
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
        print "printing: Verify pass"
        pass
