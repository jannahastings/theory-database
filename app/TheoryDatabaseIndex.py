## Searchable database index

import TheoryDatabase
from TheoryDatabase import Theory
import os


index_dir = "/data/theory-database/index"

if not os.path.exists(index_dir):
    os.mkdir(index_dir)

TheoryDatabase.setup()

TheoryDatabase.rebuildIndex(index_dir)

