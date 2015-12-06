README.txt for catalog website project

######################
## Folder Structure ##
######################
catalog:
1. database_setup.py: setup database catalogitemwithuser.db and object User, Catalog, Item
2. lotsofitem.py: Populate catalogitemwithuser.db
3. project.py: using Flask framework to define website each endpoint behavior. Access address localhost:8000

templates:
webpage templates for each endpoint to be used in project.py

static:
css file for webpage style.

################
## How to run ##
################
1. python database_setup.py # setup database catalogitemwithuser.db
2. python lotsofitem.py 	# populate database catalogitemwithuser.db
3. python project.py 		# access webpage from http://localhost:8000/

############################################
## availabe endpoints for catalog website ##
############################################
1. show all catalogs and latest 10 updated items
http://localhost:8000/ or http://localhost:8000/catalogs
2. show all items for one catalog
http://localhost:8000/catalog/<string:catalog_name>/items
3. edit one catalog (user must login)
http://localhost:8000/catalog/<string:catalog_name>/edit
4. delete one catalog (user must loging. If delete one catalog successfully, all items under this catalog will also be deleted)
http://localhost:8000/catalog/<string:catalog_name>/delete
5. create one catalog (user must login)
http://localhost:8000/catalog/new
6. show one particular item
http://localhost:8000/catalog/<string:catalog_name>/<string:item_name>
7. edit one item (user must login)
http://localhost:8000/catalog/<string:catalog_name>/<string:item_name>/edit
8 delete one item (user must login)
http://localhost:8000/catalog/<string:catalog_name>/<string:item_name>/delete
9 create one item (user must login)
http://localhost:8000/catalog/newitem
10 user login
http://localhost:8000/login
11. user logout
http://localhost:8000/disconnect
12. API json endpoint
http://localhost:8000/catalogs?format=json
http://localhost:8000/catalog/<string:catalog_name/items?format=json
http://localhost:8000/catalog/<string:catalog_name>/<string:item_name>?format=json



