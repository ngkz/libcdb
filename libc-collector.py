#!/usr/bin/python3

# depends on rpm2cpio and dpkg

import ftplib
import tempfile
import subprocess
import os
import os.path
import fnmatch
import re
import tarfile
import shlex

LIBS_DIR = os.path.join(os.path.dirname(__file__), "libs")

magic_check = re.compile('[*?[]')
def has_magic(s):
    match = magic_check.search(s)
    return match is not None

def nlst(ftp, path = ''):
    files = []
    ftp.retrlines("NLST " + path, files.append)
    return files

def decompress_rpm(dest, rpmpath):
    subprocess.check_call(
        "rpm2cpio '{0}' | (cd {1}; cpio -id) >/dev/null". \
                format(shlex.quote(rpmpath), shlex.quote(dest)),
        shell=True)

def decompress_deb(dest, debpath):
    #subprocess.check_call(["dpkg", "-x", debpath, dest])
    try:
        subprocess.check_call(
                "ar p {} data.tar.gz | tar zx -C {}".format(
                    shlex.quote(debpath),
                    shlex.quote(dest)
                ), shell=True)
    except:
        subprocess.check_call(
                "ar p {} data.tar.xz | tar Jx -C {}".format(
                    shlex.quote(debpath),
                    shlex.quote(dest)
                ), shell=True)

def decompress_xz(dest, xzpath):
    pkg = tarfile.open(xzpath, "r:xz", errorlevel=2)
    pkg.extractall(dest)

def is_libc(path):
    status = subprocess.call(
            "nm -D {} | grep __libc_start_main > /dev/null 2>&1".format(shlex.quote(path)),
            shell = True)
    return status == 0

def extract_libc(_dir):
    for root, dirs, files in os.walk(_dir):
        for name in files:
            path = os.path.join(root, name)
            if not (name.endswith(".so") and (not os.path.islink(path)) and is_libc(path)):
                #not libc
                os.unlink(path)

def get_package(ftp, url, file_handler):
    print("GET: " + url)
    pkgname = url.split("/")[-1]
    dest = os.path.join(LIBS_DIR, pkgname)
    if os.path.exists(dest):
        print("skip")
        return

    pkgfile = tempfile.NamedTemporaryFile(suffix='.deb')
    try:
        ftp.retrbinary("RETR " + url, pkgfile.write)
        pkgfile.flush()

        os.mkdir(dest)
        file_handler(dest, pkgfile.name)
        extract_libc(dest)
    except:
        pkgfile.close()
        os.rmdir(dest)
        raise

def ftp_glob_get3(ftp, url, name, patterns, file_handler):
    if len(patterns) == 0:
        get_package(ftp, url + "/" + name, file_handler)
        return

    ftp_glob_get2(ftp, url + "/" + name, list(patterns), file_handler)


def ftp_glob_get2(ftp, url, patterns, file_handler):
    pattern = patterns.pop(0)
    print("SEARCH: " + url + "/" + pattern)

    if not has_magic(pattern):
        ftp_glob_get3(ftp, url, pattern, patterns, file_handler)
        return

    try:
        ftp.sendcmd("CWD " + url)
    except ftplib.error_perm:
        return
    files = nlst(ftp)
    files = filter(lambda name: fnmatch.fnmatch(name, pattern), files)
    for name in files:
        ftp_glob_get3(ftp, url, name, patterns, file_handler)

def ftp_glob_get(server, pattern, file_handler):
    with ftplib.FTP(server) as ftp:
        ftp.login()
        ftp_glob_get2(ftp, "", pattern.split("/"), file_handler)


#debian
print("debian")
ftp_glob_get('ftp.jp.debian.org', '/debian/pool/main/e/eglibc/libc6*.deb', decompress_deb)
#ftp_glob_get('ftp.debian-ports.org', '/debian/pool*/main/e/eglibc/libc6_*.deb', decompress_deb)

#ubuntu
print("ubuntu")
ftp_glob_get('ja.archive.ubuntu.com', '/ubuntu/pool/main/e/eglibc/libc6*.deb', decompress_deb)
ftp_glob_get('ja.archive.ubuntu.com', '/ubuntu/pool/universe/*/*cross*/libc6*.deb', decompress_deb)
ftp_glob_get('ja.archive.ubuntu.com', '/ubuntu/pool/universe/g/glibc/libc6*.deb', decompress_deb)
#ftp_glob_get('ports.ubuntu.com', '/ubuntu-ports/pool/main/e/eglibc/libc6_*.deb', decompress_deb)

#centos
ftp_glob_get('ftp.jaist.ac.jp', '/pub/Linux/CentOS/*/*/*/*/glibc-[0123456789]*.rpm', decompress_rpm)

#fedora
print("fedora")
ftp_glob_get('ftp.riken.jp', '/Linux/fedora/releases/*/Everything/*/os/Packages/g/glibc-[0123456789]*.rpm', decompress_rpm)
ftp_glob_get('ftp.riken.jp', '/Linux/fedora/development/*/*/os/Packages/g/glibc-[0123456789]*.rpm', decompress_rpm)
ftp_glob_get('ftp.riken.jp', '/Linux/fedora/updates/*/*/glibc-[0123456789]*.rpm', decompress_rpm)

#arch
print("arch")
ftp_glob_get('ftp.jaist.ac.jp', '/pub/Linux/ArchLinux/pool/*/*glibc-*.tar.xz', decompress_xz)
