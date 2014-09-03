#!/usr/bin/python
import os
import os.path
import libcdb

db = libcdb.LibCDB()

for pkg in os.listdir("libs"):
    libs = []

    for root, dirs, files in os.walk(os.path.join("libs", pkg)):
        for name in files:
            path = os.path.join(root, name)
            if path.endswith(".so"):
                libs.append(path)

    print pkg, libs
    db.add_package(pkg, libs)
