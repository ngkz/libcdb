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
import sqlite3
import os.path
import subprocess
import re

def get_exports(path):
    with open(os.devnull, "wb") as null:
        output = subprocess.check_output(["nm", "-D", path], stderr = null)

    exports = {}
    for match in re.findall(r"^([0-9a-f]+) *. *(\S*)$", output.decode(),
                            re.MULTILINE | re.IGNORECASE):
        offset, name = match
        exports[name] = int(offset, 16)

    return exports

class LibCDB:
    def __init__(self, path = None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "libc.db")
        self.conn = sqlite3.connect(path)
        self.dbdir = os.path.abspath(os.path.dirname(path))
        c = self.conn.cursor()
        try:
            c.execute("""create table packages(
                name text unique not null
            )""")
            c.execute("""create table libraries(
                package_id integer not null,
                path text not null,
                unique(package_id, path)
            )""")
            c.execute("""create table symbols(
                library_id integer not null,
                name text not null,
                offset integer not null,
                unique(library_id, name)
            )""")
            c.execute("create index symbols_name on symbols(name);")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass
        c.close()

    def has_package(self, package):
        c = self.conn.cursor()
        c.execute("select exists(select name from packages where name = ?)", (package,))
        f = c.fetchone()[0] == 1
        c.close()
        return f

    def has_symbol(self, symbol):
        c = self.conn.cursor()
        c.execute("select exists(select name from symbols where name = ?)", (symbol,))
        f = c.fetchone()[0] == 1
        c.close()
        return f

    def add_package(self, package, libs):
        c = self.conn.cursor()
        c.execute("insert into packages values (?)", (package,))
        package_id = c.lastrowid

        for path in libs:
            path_dbrel = os.path.relpath(path, self.dbdir)
            c.execute("insert into libraries values (?, ?)", (package_id, path_dbrel))
            library_id = c.lastrowid

            exports = get_exports(path)
            for name, offset in exports.items():
                c.execute("insert into symbols values(?, ?, ?)", (library_id, name, offset))

        self.conn.commit()
        c.close()

    def search(self, imports):
        c = self.conn.cursor()

        conditions = []
        _vars = []
        for name, address in imports.items():
            _vars.append(name)
            _vars.append(address & 0xfff)
            conditions.append("(symbols.name = ? and symbols.offset & 4095 = ?)")
        _vars.append(len(imports.keys()))

        query = "select libraries.path from libraries, symbols where libraries.rowid = symbols.library_id and (" + " or ".join(conditions) + ") group by symbols.library_id having count(symbols.library_id) = ?"
        c.execute(query, _vars)
        result = [os.path.join(self.dbdir, row[0]) for row in c.fetchall()]
        c.close()
        return result

