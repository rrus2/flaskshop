from flask import Flask, render_template, url_for, redirect, session, request, render_template_string
from flask_pymongo import PyMongo
from wtforms import Form
import bcrypt
import os

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'shop'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/shop'
app.secret_key = 'supersecret'

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = Form(request.form)
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST' or form.validate():
        users = mongo.db.users
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        email = request.form['email']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        if not users.find_one({'username': username}) or not users.find_one({'email': email}):
            users.insert_one({'firstname': firstname, 'lastname': lastname, 'username': username, 'birthdate': birthdate, 'email': email, 'password': password})

        return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        users = mongo.db.users
        username = request.form['username']
        user = users.find_one({'username': username})
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), user['password']):
            session['username'] = username
            return render_template_string('YOU ARE LOGGED IN {}'.format(user['username']))
        else:
            return render_template_string('FAIL')

@app.route('/logout')
def logout():
    session.pop('username')
    return render_template('index.html')

@app.route('/shop')
def shop():
    collection = mongo.db.product.find()

    products = []

    for product in collection:
        products.append({'name': product['name'], 'price': product['price'], 'image': product['image']})
    
    return render_template('shop.html', products=products)

@app.route('/shopitem/<string:name>', methods = ['GET', 'POST'])
def shopitem(name):
    item = mongo.db.product.find_one({'name': name})

    return render_template('shopitem.html', item=item)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/adminusers')
def adminuser():
    return render_template('adminuser.html')

@app.route('/adminproducts', methods = ['GET', 'POST'])
def adminproducts():
    if request.method == 'GET':
        return render_template('adminproducts.html')

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']
        result = mongo.db.product.insert_one({'name': name, 'price': price, 'image': image})
        if result.acknowledged:
            return render_template('admin.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)