libcdb
======
This program allows the user to collect libc from various distributions and search for them with leaked address.

Usage
-----
.. code-block:: python

   >>> import libcdb
   >>> db = libc.db.LibCDB()
   >>> db.search({"__libc_start_main": 0x7ffff760be50})
   [u'/home/user/libcdb/libs/libc6_2.19-0ubuntu6.9_amd64.deb/lib/x86_64-linux-gnu/libc-2.19.so'] 
   >>> db.search({"printf": 0x7ffff763e340, "read": 0x7ffff76d56a0})
   [u'/home/user/libcdb/libs/libc6_2.19-0ubuntu6.9_amd64.deb/lib/x86_64-linux-gnu/libc-2.19.so']
   >>> "offset of system(): 0x{:x}".format(libcdb.get_exports('/home/user/libcdb/libs/libc6_2.19-0ubuntu6.9_amd64.deb/lib/x86_64-linux-gnu/libc-2.19.so')["system"])
   'offset of system(): 0x46590'
