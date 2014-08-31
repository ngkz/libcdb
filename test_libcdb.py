#!/usr/bin/python

import unittest
import libcdb

class HasPackageTest(unittest.TestCase):
    def setUp(self):
        self.libcdb = libcdb.LibCDB(":memory:")
        self.libcdb.add_library("libc-test1", "testlibs/testlib1.so")
        self.libcdb.add_library("libc-test2", "testlibs/testlib2.so")
        self.libcdb.add_library("libc-test3", "testlibs/testlib3.so")

    def test_has_package(self):
        self.assertEquals(self.libcdb.has_package("libc-test1"), True)
        self.assertEquals(self.libcdb.has_package("libc-test2"), True)
        self.assertEquals(self.libcdb.has_package("libc-test3"), True)
        self.assertEquals(self.libcdb.has_package("libc-test4"), False)

if __name__ == '__main__':
    unittest.main()
