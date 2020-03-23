## Searchable database index


import TheoryDatabase

index_dir = "static/index"

if not os.path.exists(index_dir):
    os.mkdir(index_dir)

TheoryDatabase.setup()

TheoryDatabase.rebuildIndex(index_dir)

