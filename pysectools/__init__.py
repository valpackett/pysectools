# -*- coding: utf-8 -*-
#
# Copyright © 2013-2014 Greg V <greg@unrelenting.technology>
#
# This work is free. You can redistribute it and/or modify it
# under the terms of the
# Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar.
# See the COPYING file for more details.
#


__all__ = [
    'cap_enter', 'drop_privileges',
    'disallow_swap', 'disallow_core_dumps',
    'zero', 'goodrandom'
]


import os
import pwd
import grp
import sys
import resource
import ctypes
import ctypes.util
import getpass
import subprocess


try:
    _LIBC = ctypes.CDLL(ctypes.util.find_library("c"))
except:
    class _LIBC(object):
        def mlockall(self, x):
            return -1


try:
    _LIBCRYPTO = ctypes.CDLL(ctypes.util.find_library("crypto"))
except:
    class _LIBCRYPTO(object):
        def arc4random_buf(self, buf, size):
            raise NotImplementedError()


def cap_enter():
    """
    Tries to enter a capability mode sandbox through the cap_enter
    call. Use it when everything the process will be doing afterwards
    is pure computation & usage of already opened file descriptors.

    Works on FreeBSD, see capsicum(4).

    Returns True if successful, False otherwise.
    """
    try:
        return _LIBC.cap_enter() != -1
    except:
        return False


def disallow_swap():
    """
    Tries to disallow memory swapping through the mlockall call
    in order to prevent secrets from leaking to the disk.

    Returns True if successful, False otherwise.
    """
    return _LIBC.mlockall(2) != -1


def disallow_core_dumps():
    """
    Disallows core dumps through the setrlimit call
    in order to prevent secrets from leaking to the disk.
    """
    return resource.setrlimit(resource.RLIMIT_CORE, [0, 0])


def zero(s):
    """
    Tries to securely erase a secret string from memory
    (overwrite it with zeros.)

    Only works on CPython.

    Returns True if successful, False otherwise.
    """
    try:
        bufsize = len(s) + 1
        offset = sys.getsizeof(s) - bufsize
        location = id(s) + offset
        ctypes.memset(location, 0, bufsize)
        return True
    except:
        return False


def drop_privileges(username=None, groupname=None):
    """
    Tries to drop the current process's privileges.

    Returns True if successful, False otherwise.
    """
    if os.getuid() != 0:  # Not root
        return False
    try:
        # Remove group privileges
        os.setgroups([])
        # Try setting the new uid/gid
        if username and username != "":
            os.setuid(pwd.getpwnam(username).pw_uid)
        if groupname and groupname != "":
            os.setgid(grp.getgrnam(groupname).gr_gid)
        return True
    except OSError:
        return False


def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def pinentry(prompt="Enter the password: ", description=None,
             error="Wrong password!",
             pinentry_path="pinentry",
             validator=lambda x: x is not None,
             fallback_to_getpass=True):
    """
    Gets a password from the user using the pinentry program, which usually
    comes with GnuPG.

    Supports both curses and GUI versions, and fallback to Python's getpass.

    Expect all the exceptions in case something goes wrong!
    """

    if not cmd_exists(pinentry_path):
        if fallback_to_getpass and os.isatty(sys.stdout.fileno()):
            if description:
                print description
            password = None
            while not validator(password):
                if password is not None:
                    print error
                password = getpass.getpass(prompt)
            return password
        else:
            return None

    p = subprocess.Popen(pinentry_path,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         close_fds=True)

    def waitfor(what):
        out = ""
        while not out.startswith(what):
            out = p.stdout.readline()
        return out

    def comm(x):
        p.stdin.write(x + "\n")
        waitfor("OK")

    waitfor("OK")
    esc = lambda x: x.replace("%", "%25").replace("\n", "%0A")
    env = os.environ.get
    comm("OPTION lc-ctype=%s" % env('LC_CTYPE', env('LC_ALL', 'en_US.UTF-8')))
    comm("OPTION ttyname=%s" % env('TTY', os.ttyname(sys.stdout.fileno())))
    if env('TERM'):
        comm("OPTION ttytype=%s" % env('TERM'))
    if prompt:
        comm("SETPROMPT %s" % esc(prompt))
    if description:
        comm("SETDESC %s" % esc(description))
    password = None
    while not validator(password):
        if password is not None:
            comm("SETERROR %s" % esc(error))
        p.stdin.write("GETPIN\n")
        password = waitfor("D ")[2:].replace("\n", "")
    p.kill()
    return password


def goodrandom(size=64):
    """
    Generates a cryptographically secure pseudorandom byte string of the
    given size (in bytes).

    If libcrypto has arc4random_buf (LibreSSL), it will be used.
    Otherwise, it tries os.urandom and then libc/arc4random_buf (*BSD).

    If everything fails, returns False.
    """

    buf = ctypes.create_string_buffer("\000" * size)
    try:
        _LIBCRYPTO.arc4random_buf(buf, size)
        return buf.value
    except:
        try:
            return os.urandom(size)
        except:
            try:
                _LIBC.arc4random_buf(buf, size)
                return buf.value
            except:
                return False
    return False
