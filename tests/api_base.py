
import unittest

from lueftungstool import create_app

class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
