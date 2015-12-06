from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User

#Connect to Database and create database session
engine = create_engine('sqlite:///catalogitemwithuser.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#NEW imports for this step
from flask import session as login_session
import random, string

##
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from datetime import datetime

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']


##login
@app.route('/login')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
  login_session['state'] = state
  return render_template('login.html', STATE=state)

##google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        # print 'credentials: ', credentials, credentials.__dict__
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # print result
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    login_session['access_token'] = access_token
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # user_id = getUserID(login_session['email'])
    # if user_id is None:
    #   user_id = createUser(login_session)
    # login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!", output
    return output

# disconnect
@app.route('/disconnect')
def disconnect():
	print login_session
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(json.dumps('Current user is not connected!'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	del login_session['access_token']
	del login_session['gplus_id']
	del login_session['username']
	del login_session['email']
	del login_session['picture']
	if result['status'] == '200':
	  flash('Successfully disconnected!')
	else:
	  flash('Failed to revoke token for given user from Google. But Logout OK.')
	return redirect(url_for('showCatalogs'))

# homepage. Show all catalogs and latest updated 10 items
# support API endpoint /catalogs?format=json
@app.route('/')
@app.route('/catalogs')
def showCatalogs():
	return_json = request.args.get('format')
	catalogs = session.query(Catalog).order_by(asc(Catalog.name))
	items = session.query(Item).order_by(desc(Item.last_update_time)).limit(10).all()
	if return_json != 'json':
		return render_template('catalogs.html', catalogs=catalogs, items=items)
	else:
		return jsonify(Category=[i.serialize for i in catalogs])

# create a new catalog. Duplicate catalog name is not supported.
# if duplicate catalog name is detected in database, will flash error message
# if user is not login, will redirect to login page
@app.route('/catalog/new', methods=['GET', 'POST'])
def newCatalog():
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	if request.method == 'POST':
		new_catalog_name = (request.form['name']).strip()
		## check if there is duplicated catalog name
		exist_catalog_query = session.query(Catalog).filter_by(name=new_catalog_name).all()
		if exist_catalog_query:
			flash('Error: catalog %s already existed in database!'%new_catalog_name)
		else:
			user_id = getUserID(login_session.get('email'))
			# if login user is not existed in database, will create user
			if user_id is None:
				user_id = createUser(login_session)
			newCatalog = Catalog(name=new_catalog_name, user_id=user_id)
			session.add(newCatalog)
			session.commit()
			flash('New Catalog %s successfully created!' % newCatalog.name)
		return redirect(url_for('showCatalogs'))
	else:
		return render_template('newCatalog.html')

# edit catalog
# if user is not login, will redirect to login page.
@app.route('/catalog/<string:catalog_name>/edit', methods=['GET', 'POST'])
def editCatalog(catalog_name):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	user_id = getUserID(login_session['email'])
	to_edit_catalogs = session.query(Catalog).filter_by(name=catalog_name).all()
	# if no catalog is found for such catalog name
	if not to_edit_catalogs:
		flash('This catalog %s does not exist!' % catalog_name)
		return redirect(url_for('showCatalogs'))
	assert len(to_edit_catalogs) == 1
	to_edit_catalog = to_edit_catalogs[0]
	# if login user does not have permission to edit this catalog
	if to_edit_catalog.user_id != user_id:
		flash("You don't have permission to edit this catalog")
		return redirect(url_for('showCatalogs'))
	old_name = to_edit_catalog.name
	if request.method == 'POST':
		if request.form['name']:
			to_edit_catalog.name = request.form['name']
			new_name = request.form['name']
			session.add(to_edit_catalog)
			session.commit()
			flash('Catalog name successfully edited from %s to %s' %(old_name, new_name))
		return redirect(url_for('showCatalogs'))
	else:
		return render_template('editCatalog.html', catalog=to_edit_catalog)

# delete catalog
# will redict user to homepage if user not login yet.
@app.route('/catalog/<string:catalog_name>/delete', methods=['GET', 'POST'])
def deleteCatalog(catalog_name):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	user_id = getUserID(login_session['email'])
	to_delete_catalogs = session.query(Catalog).filter_by(name=catalog_name).all()
	# if such catalog name cannot be found in database
	if not to_delete_catalogs:
		flash ('This catalog %s does not exist!' % catalog_name)
		return redirect(url_for('showCatalogs'))
	assert len(to_delete_catalogs) == 1
	# if user does not have permission to edit such catalog
	to_delete_catalog = to_delete_catalogs[0]
	if to_delete_catalog.user_id != user_id:
		flash ("You don't have permission to delete this catalog")
		return redirect(url_for('showCatalogs'))
	if request.method == 'POST':
		items = session.query(Item).filter_by(catalog_id=to_delete_catalog.id).all()
		# print items
		session.delete(to_delete_catalog)
		# delete all the items belongs to this catalog
		for i in items:
			print i.name
			session.delete(i)
		session.commit()
		flash('%s has successfully deleted!' % to_delete_catalog.name)
		return redirect(url_for('showCatalogs'))
	else:
		return render_template('deleteCatalog.html', catalog=to_delete_catalog)


# show all the items in one catalog
# support API endpoint /catalog/<string:catalog_name/items?format=json
@app.route('/catalog/<string:catalog_name>/items')
def showItem(catalog_name):
	user_id = getUserID(login_session.get('email'))
	return_json = request.args.get('format')

	catalogs = session.query(Catalog).filter_by(name=catalog_name).order_by(asc(Catalog.name)).all()
	# if not catalog found for this catalog_name, will redirect to homepage
	if not catalogs:
		flash("This catalog %s does not exist!" % catalog_name)
		return redirect(url_for("showCatalogs"))
	assert len(catalogs) == 1
	catalog = catalogs[0]
	items = session.query(Item).filter_by(catalog_id=catalog.id).all()
	catalogs = session.query(Catalog).order_by(asc(Catalog.name)).all()
	if return_json != 'json':
		return render_template('items.html', items=items, catalog=catalog, user_id=user_id, catalogs=catalogs)
	else:
		return jsonify(Category=catalog.serialize)


# show one item
# support API endpoint /catalog/<string:catalog_name>/<string:item_name>?format=json
@app.route('/catalog/<string:catalog_name>/<string:item_name>')
def showOneItem(catalog_name, item_name):
	user_id = getUserID(login_session.get('email'))
	return_json = request.args.get('format')

	catalogs = session.query(Catalog).filter_by(name=catalog_name).order_by(asc(Catalog.name)).all()
	# if not catalog found for this catalog_name, will redirect to homepage
	if not catalogs:
		flash("This catalog %s does not exist!" % catalog_name)
		return redirect(url_for("showCatalogs"))
	assert len(catalogs) == 1
	catalog = catalogs[0]
	items = session.query(Item).filter_by(name=item_name).filter_by(catalog_id=catalog.id).all()
	# if not item found for this item_name, will redirect to homepage
	if not items:
		flash("This item %s does not exist!" % item_name)
		return redirect(url_for('showCatalogs'))
	item = items[0]
	if return_json != 'json':
		return render_template('oneItem.html', item=item, catalog=catalog, user_id=user_id)
	else:
		return jsonify(Item=item.serialize)


# create one item
# if user is not login, will redirect to login page.
@app.route('/catalog/newitem', methods=['GET', 'POST'])
def newItem():
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	catalogs = session.query(Catalog).order_by(asc(Catalog.name)).all()
	user_id = getUserID(login_session['email'])
	#if login user is not exist, will create user
	if user_id is None:
		user_id = createUser(login_session)
	if request.method == 'POST':
		new_item_name=request.form['name'].strip()
		exist_items = session.query(Item).filter_by(name=new_item_name).filter_by(catalog_id=request.form['catalog_id']).all()
		# if duplicate item name is found within same catalog, will flash error.
		if exist_items:
			flash('Error: item %s already existed in database!' % new_item_name)
		else:
			newItem = Item(name=new_item_name, description=request.form['description'], catalog_id=request.form['catalog_id'], user_id = user_id)
			session.add(newItem)
			session.commit()
			flash('New Item %s has successfully created!'%newItem.name)
		return redirect(url_for('showCatalogs'))
	else:
		return render_template('newItem.html', catalogs=catalogs)


# edit one item
# if user is not login, will redirect to login page.
@app.route('/catalog/<string:catalog_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(catalog_name, item_name):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	# check if catalog and item can be found in database
	catalogs=session.query(Catalog).order_by(asc(Catalog.name)).all()
	catalog_all = session.query(Catalog).filter_by(name=catalog_name).all()
	if not catalog_all:
		flash ('This catalog %s does not exist!' % catalog_name)
		return redirect(url_for('showCatalogs'))
	assert len(catalog_all) == 1
	catalog = catalog_all[0]
	to_edit_items=session.query(Item).filter_by(name=item_name).filter_by(catalog_id=catalog.id).all()
	if not to_edit_items:
		flash ('This item %s does not exist!' % item_name)
	assert len(to_edit_items) == 1
	to_edit_item = to_edit_items[0]
	user_id = getUserID(login_session.get('email'))
	# check if user has permission to edit this item. Only creator can edit item.
	if to_edit_item.user_id != user_id:
		flash("You don't have permission to edit this item")
		return redirect(url_for('showCatalogs'))
	if request.method == 'POST':
		if request.form['name']:
			to_edit_item.name = request.form['name']
		if request.form['description']:
			to_edit_item.description = request.form['description']
		if request.form['catalog_id']:
			to_edit_item.catalog_id = request.form['catalog_id']
		to_edit_item.last_update_time = datetime.now()
		session.add(to_edit_item)
		session.commit()
		flash("Item has successfully edited!")
		return redirect(url_for('showItem', catalog_name=catalog_name))
	else:
		return render_template('editItem.html', item=to_edit_item, catalogs=catalogs, catalog=catalog)


# delete item
# if user is not login, will redirect to login page.
@app.route('/catalog/<string:catalog_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(catalog_name, item_name):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))

	## check if catalog and item can be found in database
	catalogs=session.query(Catalog).order_by(asc(Catalog.name)).all()
	catalog_all = session.query(Catalog).filter_by(name=catalog_name).all()
	if not catalog_all:
		flash ('This catalog %s does not exist!' % catalog_name)
		return redirect(url_for('showCatalogs'))
	assert len(catalog_all) == 1
	catalog = catalog_all[0]

	to_delete_items=session.query(Item).filter_by(name=item_name).filter_by(catalog_id=catalog.id).all()
	if not to_delete_items:
		flash ('This item %s does not exist!' % item_name)
		return redirect(url_for('showCatalogs'))
	to_delete_item = to_delete_items[0]
	user_id = getUserID(login_session.get('email'))
	# check if user has permission to delete this item. Only creator can delete item.
	if to_delete_item.user_id != user_id:
		flash("You don't have permission to delete this item")
		return redirect(url_for('showCatalogs'))
	if request.method == 'POST':
		session.delete(to_delete_item)
		session.commit()
		flash('Item %s has successfully deleted!'%to_delete_item.name)
		return redirect(url_for('showItem', catalog_name=catalog_name))
	else:
		return render_template('deleteItem.html', item=to_delete_item, catalog=catalog)

# get user_id from email address. If no user found, return None
def getUserID(email):
	user_query = session.query(User).filter_by(email=email).all()
	if len(user_query) == 0:
		return None
	else:
		return user_query[0].id

# return user from user_id
def getUserInfo(user_id):
  user = session.query(User).filter_by(id=user_id).one()
  return user

# create user from login_session, return user_id
def createUser(login_session):
  newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
  session.add(newUser)
  session.commit()
  user=session.query(User).filter_by(email=login_session['email']).one()
  return user.id

## access port localhost:8000

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)