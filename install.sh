#!/bin/bash

zip chaido.zip __main__.py chaido.py version.py data_migration.py Exceptions.py
echo '#!/usr/bin/python3' | cat - chaido.zip > /usr/bin/chaido
chmod 755 /usr/bin/python3
rm chaido.zip
