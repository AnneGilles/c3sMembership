#!/bin/bash

echo "extracting message strings..."
env/bin/python setup.py extract_messages
echo "updating po files..."
env/bin/python setup.py update_catalog
echo "edit with POEDIT or transifex <-- TODO!"
# TODO :-)
echo "compiling catalog (POEDIT does this anyways)"
env/bin/python setup.py compile_catalog
echo "done. restart pyramid to see effects"
