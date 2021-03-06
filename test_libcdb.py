#!/usr/bin/python
"""
    libcdb
    Copyright (C) 2014-2017  Kazutoshi Noguchi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import libcdb
import os

class LibcDBTest(unittest.TestCase):
    def setUp(self):
        self.libcdb = libcdb.LibCDB(":memory:")
        self.libcdb.add_package("libc-test12", ["testlibs/testlib1.so",
                                                "testlibs/testlib2.so"])
        self.libcdb.add_package("libc-test3", ["testlibs/testlib3.so"])
        self.libcdb.add_package("libc-test4", [])

    def test_has_package(self):
        self.assertEqual(self.libcdb.has_package("libc-test12"), True)
        self.assertEqual(self.libcdb.has_package("libc-test3"), True)
        self.assertEqual(self.libcdb.has_package("libc-test4"), True)
        self.assertEqual(self.libcdb.has_package("libc-test5"), False)

    def test_search(self):
        self.assertEqual(self.libcdb.search({
            "__libc_start_main": 0x55555320
        }), [
            os.path.abspath("testlibs/testlib1.so"),
            os.path.abspath("testlibs/testlib2.so")
        ])
        self.assertEqual(self.libcdb.search({
            "a": 0x55555320
        }), [])
        self.assertEqual(self.libcdb.search({
            "__libc_start_main": 0x55555273
        }), [os.path.abspath("testlibs/testlib3.so")])
        self.assertEqual(self.libcdb.search({
            "__libc_start_main": 0x55555320,
            "write": 0x55555321
        }), [os.path.abspath("testlibs/testlib1.so")])
        self.assertEqual(self.libcdb.search({
            "__libc_start_main": 0x55555320,
            "write": 0x55555322
        }), [os.path.abspath("testlibs/testlib2.so")])

    def test_has_symbol(self):
        self.assertTrue(self.libcdb.has_symbol("this_is_testlib1"))
        self.assertTrue(self.libcdb.has_symbol("this_is_testlib2"))
        self.assertFalse(self.libcdb.has_symbol("AAAAAAAAAAAAAAAAAAA"))

class LibcDBPathTest(unittest.TestCase):
    def test_path(self):
        db = libcdb.LibCDB(":memory:")
        os.chdir("testlibs")
        try:
            db.add_package("libc-test1", ["testlib1.so"])
        finally:
            os.chdir("..")

        self.assertEqual(db.search({
            "__libc_start_main": 0x55555320
        }), [os.path.abspath("testlibs/testlib1.so")])

if __name__ == '__main__':
    unittest.main()
