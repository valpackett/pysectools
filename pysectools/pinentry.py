# -*- coding: utf-8 -*-
#
# Copyright © 2013-2014 Greg V <greg@unrelenting.technology>
#
# This work is free. You can redistribute it and/or modify it
# under the terms of the
# Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar.
# See the COPYING file for more details.

from __future__ import print_function

import os
import sys
import getpass
import subprocess


def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


class PinentryException(Exception): pass
class PinentryUnavailableException(PinentryException): pass
class PinentryClosedException(PinentryException): pass


class Pinentry(object):

    def __init__(self, pinentry_path="pinentry", fallback_to_getpass=True):
        if not cmd_exists(pinentry_path):
            if fallback_to_getpass and os.isatty(sys.stdout.fileno()):
                self._ask = self._ask_with_getpass
                self._close = self._close_getpass
            else:
                raise PinentryUnavailableException()
        else:
            self.process = subprocess.Popen(pinentry_path,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            close_fds=True)
            self._ask = self._ask_with_pinentry
            self._close = self._close_pinentry
        self._closed = False

    def ask(self, prompt="Enter the password: ", description=None,
            error="Wrong password!",
            validator=lambda x: x is not None):
        if self._closed:
            raise PinentryClosedException()
        return self._ask(prompt, description, error, validator)

    def close(self):
        self._closed = True
        return self._close()

    def _ask_with_getpass(self, prompt, description, error, validator):
        if description:
            print(description)
        password = None
        while not validator(password):
            if password is not None:
                print(error)
            password = getpass.getpass(prompt)
        return password

    def _close_getpass(self): pass

    def _ask_with_pinentry(self, prompt, description, error, validator):
        self._waitfor("OK")
        env = os.environ.get
        self._comm("OPTION lc-ctype=%s" % env("LC_CTYPE", env("LC_ALL", "en_US.UTF-8")))
        try:
            self._comm("OPTION ttyname=%s" % env("TTY", os.ttyname(sys.stdout.fileno())))
        except:
            pass
        if env('TERM'):
            self._comm("OPTION ttytype=%s" % env("TERM"))
        if prompt:
            self._comm("SETPROMPT %s" % self._esc(prompt))
        if description:
            self._comm("SETDESC %s" % self._esc(description))
        password = None
        while not validator(password):
            if password is not None:
                self._comm("SETERROR %s" % self._esc(error))
            self.process.stdin.write("GETPIN\n")
            password = self._waitfor("D ")[2:].replace("\n", "")
        return password

    def _close_pinentry(self):
        return self.process.kill()

    def _waitfor(self, what):
        out = ""
        while not out.startswith(what):
            out = self.process.stdout.readline()
        return out

    def _comm(self, x):
        self.process.stdin.write(x + "\n")
        self._waitfor("OK")

    def _esc(self, x):
        return x.replace("%", "%25").replace("\n", "%0A")
