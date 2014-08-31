#!/usr/bin/python

import unittest
import libcdb

class LibcDBTest(unittest.TestCase):
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

    def test_search(self):
        self.assertEquals(self.libcdb.search({
            "__libc_start_main": 0x55555320
        }), ["testlibs/testlib1.so", "testlibs/testlib2.so"])
        self.assertEquals(self.libcdb.search({
            "a": 0x55555320
        }), [])
        self.assertEquals(self.libcdb.search({
            "__libc_start_main": 0x55555273
        }), ["testlibs/testlib3.so"])
        self.assertEquals(self.libcdb.search({
            "__libc_start_main": 0x55555320,
            "write": 0x55555321
        }), ["testlibs/testlib1.so"])
        self.assertEquals(self.libcdb.search({
            "__libc_start_main": 0x55555320,
            "write": 0x55555322
        }), ["testlibs/testlib2.so"])

if __name__ == '__main__':
    unittest.main()
