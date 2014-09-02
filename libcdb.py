import sqlite3
import os.path
import subprocess
import re

def get_exports(path):
    with open(os.devnull, "wb") as null:
        output = subprocess.check_output(["nm", "-D", path], stderr = null)

    exports = {}
    for match in re.findall(r"^([0-9a-f]+) *. *(\S*)$", output,
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
            c.execute("""create table libraries(
                package text not null,
                path text not null,
                unique(package, path)
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
        c.execute("select exists(select package from libraries where package = ?)", (package,))
        f = c.fetchone()[0] == 1
        c.close()
        return f

    def add_library(self, package, path):
        path_dbrel = os.path.relpath(path, self.dbdir)
        c = self.conn.cursor()
        c.execute("insert into libraries (package, path) values (?, ?)", (package, path_dbrel))
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

