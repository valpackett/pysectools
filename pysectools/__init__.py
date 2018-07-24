# -*- coding: utf-8 -*-

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
    if os.geteuid() != 0:  # Not root
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


def _force_arc4random(lib, buf, size):
    """
    Calls arc4random_buf on a buffer until it worked correctly.
    (On Apple OS X, len(buf.value) is VERY OFTEN not equal to the given size)
    """

    while len(buf.value) != size:
        lib.arc4random_buf(buf, size)
    return buf.value


def goodrandom(size=64):
    """
    Generates a cryptographically secure pseudorandom byte string of the
    given size (in bytes).

    It tries os.urandom first, then libcrypto/arc4random_buf (LibreSSL?) and then libc/arc4random_buf (*BSD).

    If everything fails, returns False.
    """

    buf = ctypes.create_string_buffer(b"\000" * size)
    try:
        return os.urandom(size)
    except:
        try:
            _force_arc4random(_LIBCRYPTO, buf, size)
            return buf.value
        except:
            try:
                _force_arc4random(_LIBC, buf, size)
                return buf.value
            except:
                return False
    return False
