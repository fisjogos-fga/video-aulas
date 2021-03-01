import unittest

class TestClass(unittest.TestCase):
    def test_something(self):
        a, b = 1, 2 
        assert a + b == 3