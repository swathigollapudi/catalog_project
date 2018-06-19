from flask import Flask
import render_template
import request
import redirect
import jsonify
import url_for
import flash


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from myproject import Base, Onlineshopping, Products, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///shopping.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response
        (json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '\" style = \"width: 300px;'
    output += 'height: 300px;'
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/shoppingwebsite/<int:shoppingwebsite_id>/product/JSON')
def shoppingwebsiteproductJSON(shoppingwebsite_id):
    shoppingwebsite = session.query(Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    products = session.query(Products).filter_by(
        shoppingwebsite_id=shoppingwebsite_id).all()
    return jsonify(Products=[i.serialize for i in products])


@app.route('/ shoppingwebsite/<int: shoppingwebsite_id >/ product / <int: product_id > /JSON')
def menuItemJSON(shoppingwebsite_id, product_id):
    Menu_Products = session.query(Products).filter_by(id=product_id).one()
    return jsonify(Menu_Products=Menu_Products.serialize)


@app.route('/shoppingwebsite/JSON')
def shoppingwebsitesJSON():
    shoppingwebsites = session.query(Onlineshopping).all()
    return jsonify(shoppingwebsites=[r.serialize for r in shoppingwebsites])


@app.route('/')
@app.route('/shoppingwebsite/')
def showshoppingwebsites():

    session = DBSession()
    shoppingwebsites = session.query(Onlineshopping).order_by(asc(Onlineshopping.name))
    session.close()
    return render_template('shoppingwebsites.html', shoppingwebsites=shoppingwebsites)
@app.route('/shoppingwebsite/new/', methods=['GET', 'POST'])
def newOnlineshopping():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newOnlineshopping = Onlineshopping(
            name=request.form['name'])
        session.add(newOnlineshopping)
        flash
        ('New Onlineshopping %s Successfully Created' % newOnlineshopping.name)
        session.commit()
        return redirect(url_for('showshoppingwebsites'))
    else:
        return render_template('newshoppingwebsite.html')


@app.route('/shoppingwebsite/<int:shoppingwebsite_id>/edit/', methods=['GET', 'POST'])


def editOnlineshopping(shoppingwebsite_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedOnlineshopping = session.query(
        Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedOnlineshopping.name = request.form['name']
            session.add(editedOnlineshopping)
            session.commit()
            flash
            ('Onlineshopping Successfully Edited %s'
             % editedOnlineshopping.name)
            return redirect(url_for('showshoppingwebsites'))
    else:
        return
        render_template('editShoppingwebsite.html', shoppingwebsite=editedOnlineshopping)


@app.route('/shoppingwebsite/<int:shoppingwebsite_id>/delete/', methods=['GET', 'POST'])


def deleteOnlineshopping(shoppingwebsite_id):
    if 'username' not in login_session:
        return redirect('/login')
    shoppingwebsiteToDelete = session.query(Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    if request.method == 'POST':
        session.delete(shoppingwebsiteToDelete)
        flash('%s Successfully Deleted' % shoppingwebsiteToDelete.name)
        session.commit()
        return
        redirect(url_for('showshoppingwebsites', shoppingwebsite_id=shoppingwebsite_id))
    else:
        return
        render_template ('deleteshoppingwebsite.html', shoppingwebsite=shoppingwebsiteToDelete)
@app.route('/shoppingwebsite/<int:shoppingwebsite_id>/')
@app.route('/shoppingwebsite/<int:shoppingwebsite_id>/product/')
def showProduct(shoppingwebsite_id):
    shoppingwebsite = session.query(Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    products = session.query(Products).filter_by(shoppingwebsite_id=shoppingwebsite_id).all()
    return
    render_template('product.html', products=products, shoppingwebsite=shoppingwebsite)


@app.route('/shoppingwebsite/<int:shoppingwebsite_id>/product/new/',
 methods=['GET', 'POST'])


def newProducts(shoppingwebsite_id):
    if 'username' not in login_session:
        return redirect('/login')
    shoppingwebsite = session.query(Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    if request.method == 'POST':
        newProduct = Products(name=request.form['name'], price=request.form['price'], course=request.form['course'],shoppingwebsite_id=shoppingwebsite_id,user_id=shoppingwebsite.user_id)
        session.add(newProduct)
        session.commit()
        flash('New Product %s Item Successfully Created' % (newProduct.name))
        return
        redirect(url_for('showProduct', shoppingwebsite_id=shoppingwebsite_id))
    else:
        return
        render_template('newproduct.html', shoppingwebsite_id=shoppingwebsite_id)


@app.route
('/shoppingwebsite/<int:shoppingwebsite_id>/product/<int:product_id>/edit',
    methods=['GET', 'POST'])


def editProducts(shoppingwebsite_id, product_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedProduct = session.query(Products).filter_by(id=product_id).one()
    shoppingwebsite =
    session.query(Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedProduct.name = request.form['name']
        if request.form['price']:
            editedProduct.price = request.form['price']
        if request.form['course']:
            editedProduct.course = request.form['course']
        session.add(editedProduct)
        session.commit()
        flash('Products Successfully Edited')
        return
        redirect(url_for('showProduct', shoppingwebsite_id=shoppingwebsite_id))
    else:
        return
        render_template('editproduct.html',shoppingwebsite_id=shoppingwebsite_id,product_id=product_id, product=editedProduct)


@app.route('/ shoppingwebsite / < int: shoppingwebsite_id > / product /
     <int: product_id > /delete', methods=['GET', 'POST'])


def deleteProducts(shoppingwebsite_id, product_id):

    if 'username' not in login_session:
        return redirect('/login')
    shoppingwebsite =session.query(Onlineshopping).filter_by(id=shoppingwebsite_id).one()
    ProductToDelete = session.query(Products).filter_by(id=product_id).one()
    if request.method == 'POST':
        session.delete
        (ProductToDelete)
        session.commit()
        flash('Product Successfully Deleted')
        return redirect(url_for('showProduct', shoppingwebsite_id=shoppingwebsite_id))
    else:
        return render_template('deleteproduct.html', product=ProductToDelete)
    if __name__ == '__main__':
        app.secret_key = 'super_secret_key'
        app.debug = True
        app.run(host='0.0.0.0', port=5000)
