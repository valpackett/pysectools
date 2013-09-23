# -*- coding: utf-8 -*-
#
# Copyright © 2013 Greg V <floatboth@me.com>
#
# This work is free. You can redistribute it and/or modify it
# under the terms of the
# Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar.
# See the COPYING file for more details.
#

__all__ = ['zero', 'disallow_swap', 'disallow_core_dumps',
        'drop_privileges']

import os
import pwd
import grp
import sys
import resource
import ctypes
import ctypes.util

try:
    _LIBC = ctypes.CDLL(ctypes.util.find_library("c"))
except:
    class _LIBC(object):
        def mlockall(self, x):
            return -1


def disallow_swap():
    """
    Tries to disallow memory swapping through the mlockall call
    in order to prevent secrets from leaking to the disk.

    Returns True if successful, False otherwise.
    """
    if _LIBC.mlockall(2) == -1:
        return False
    return True


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
