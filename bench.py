#!/usr/bin/python
import libcdb
db = libcdb.LibCDB()
for i in range(1000):
    db.search({"__libc_start_main":0x400990, "write": 0xdb530})
