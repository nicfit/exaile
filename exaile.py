#!/usr/bin/env python
# Copyright (C) 2008-2010 Adam Olsen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import os
import os.path
import sys

# allow disabling of pyc generation. Only works on python >= 2.6
if os.getenv("EXAILE_NO_OPTIMIZE"):
    try:
        sys.dont_write_bytecode = True
    except:
        pass

if sys.platform == 'linux2':
    # Set process name.  Only works on Linux >= 2.1.57.
    try:
        import ctypes
        libc = ctypes.CDLL('libc.so.6')
        libc.prctl(15, 'exaile', 0, 0, 0) # 15 = PR_SET_NAME
    except:
        pass

# Find out the location of exaile's working directory, and insert it to sys.path
basedir = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(basedir, "exaile.py")):
    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, "exaile.py")):
        basedir = cwd
sys.path.insert(0, basedir)

def main():
    from xl import main
    global exaile
    exaile = main.Exaile()

if __name__ == "__main__":
    main()

# vim: et sts=4 sw=4
