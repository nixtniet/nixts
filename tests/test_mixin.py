# This file is placed in the Public Domain.


"mixin"


import unittest


from nixts.objects import Object


class Mix:

    a = "b"


class Mixin(Mix, Object):

    pass


class TestMixin(unittest.TestCase):

    def test_mixin(self):
        mix = Mixin()
        self.assertTrue(isinstance(mix, Mixin))
