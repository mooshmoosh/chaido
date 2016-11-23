#!/bin/bash

zip chaido.zip __main__.py chaido.py version.py data_migration.py Exceptions.py

# I know... this is hax. The header for zip files is at the end, so you
# can put whatever crap at the start of the file and it all just works.
# In this case we put a shebang. Python will happily open a zip file and
# execute the __main__.py script inside it. You can import any other
# modules relative to __main__.py
echo '#!/usr/bin/python3' | cat - chaido.zip > /usr/bin/chaido

chmod 755 /usr/bin/python3
rm chaido.zip
