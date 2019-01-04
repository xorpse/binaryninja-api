#!/usr/bin/env python
#
#    Thanks to @withzombies for letting us adapt his script
#

import sys
import os
from site import getsitepackages, getusersitepackages, check_enableusersite

# Hacky command line parsing to accept a silent-install -s flag like linux-setup.sh:
INTERACTIVE = True
if '-s' in sys.argv[1:]:
    INTERACTIVE = False

try:
    import binaryninja
    print("Binary Ninja API already Installed")
    sys.exit(1)
except ImportError:
    pass

if sys.platform.startswith("linux"):
    user_path =  os.path.expanduser("~/.binaryninja")
elif sys.platform == "darwin":
    user_path = os.path.expanduser("~/Library/Application Support/Binary Ninja")
else:
    user_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Vector35", "BinaryNinja")
lastrun = os.path.join(user_path, "lastrun")

if os.path.isfile(lastrun):
    lastrunpath = open(lastrun).read().strip()
    api_paths = [ os.path.join(lastrunpath, "python") ]
    print("Found lastrun pointing to {}".format(api_paths[0]))
else:
    api_paths = []

if sys.platform.startswith("linux"):
    if len(api_paths) == 0:
        api_paths = [ os.path.expanduser("~/binaryninja/python") ]
    else:
        api_paths[0] = os.path.join(api_paths[0], "python")
elif sys.platform == "darwin":
    if len(api_paths) > 0:
        api_paths[0] = [ os.path.join(api_paths[0], "..", "..", "Resources", "python") ]
    api_paths.insert(0, "/Applications/Binary Ninja.app/Contents/Resources/python") #as a backup if lastrun is wrong
else:
    # Windows
    if len(api_paths) > 0:
        api_paths[0] = [ os.path.join(api_paths[0], "python") ]
    api_paths.insert(0, "r'C:\Program Files\Vector35\BinaryNinja\python'")
    api_paths.insert(0, os.path.join(os.getenv("APPDATA"), "..", "Local", "Vector35", "BinaryNinja", "python"))

def validate_path(path):
    try:
        os.stat(path)
    except OSError:
        return False

    old_path = sys.path
    sys.path.append(path)

    try:
        from binaryninja import core_version
        print("Found Binary Ninja core version: {}".format(core_version()))
    except ImportError:
        sys.path = old_path
        return False

    return True

while len(api_paths) > 0:
    api_path = api_paths.pop()
    if validate_path(api_path):
        break
else:
    while True:
        print("\nBinary Ninja not found.")
        if not INTERACTIVE:
            print("Non-interactive mode selected, failing.")
            sys.exit(-1)

        print("Please provide the path to Binary Ninja's install directory or python folder: \n [{}] : ".format(api_path))
        new_path = os.path.expanduser(sys.stdin.readline().strip())
        if len(new_path) == 0:
            print("\nInvalid path")
            continue

        if not new_path.endswith('python'):
            new_path = os.path.join(new_path, 'python')

        api_path = new_path
        if validate_path(api_path):
            break

if ( len(sys.argv) > 1 and sys.argv[1].lower() == "root" ):
    #write to root site
    install_path = getsitepackages()[0]
    if not os.access(install_path, os.W_OK):
        print("Root install specified but cannot write to {}".format(install_path))
        sys.exit(1)
else:
    if check_enableusersite():
        install_path = getusersitepackages()
        if not os.path.exists(install_path):
            os.makedirs(install_path)
    else:
        print("Warning, trying to write to user site packages, but check_enableusersite fails.")
        sys.exit(1)

binaryninja_pth_path = os.path.join(install_path, 'binaryninja.pth')
open(binaryninja_pth_path, 'wb').write(api_path.encode('charmap'))

print("Binary Ninja API installed using {} pointing to {}".format(binaryninja_pth_path, api_path))
