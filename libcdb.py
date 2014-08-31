import sqlite3
import os.path

class LibCDB:
    def __init__(self, path = None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "libc.db")
        self.conn = sqlite3.connect(path)
        c = self.conn.cursor()
        try:
            c.execute("""create table libraries(
                id integer primary key autoincrement,
                package text unique not null,
                path text unique not null
            )""")
            c.execute("""create table symbols(
                library_id integer not null,
                name text not null,
                offset integer not null,
                unique(library_id, name)
            )""")
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
        c = self.conn.cursor()
        c.execute("insert into libraries (package, path) values (?, ?)", (package, path))
        self.conn.commit()
        c.close()

    def search(self, imports):
        pass

