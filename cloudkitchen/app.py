from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
import database as db
import authentication
import logging
import ordermanagement as om


app = Flask(__name__)

app.secret_key = b's@g@d@c0ff33!'
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)
#============================================LOG IN CODE =====================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/login_error')
def login_error():
    loginerror = "Incorrect username or password.Please try again"
    return render_template('/login.html', loginerror = loginerror)

    
@app.route('/auth', methods = ['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return redirect('/login_error')
#===================================LOG IN=====================================================
@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_product()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    
    return render_template('productdetails.html', code=code, product=product)

@app.route('/bigfat')
def bigfat():
    product_list=db.get_bigfat()
    bigfat = request.args.get('bigfat_coll')

    return render_template('bigfat.html', page="Products", product_list=product_list)

@app.route('/caged')
def caged():
    product_list=db.get_caged()
    caged = request.args.get('caged_coll')
    
    return render_template('caged.html', page="Products", product_list=product_list)

@app.route('/taverna')
def taverna():
    product_list=db.get_taverna()
    taverna = request.args.get('taverna_coll')
    
    return render_template("taverna.html", page="Products", product_list=product_list)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/howtouse')
def howtouse():
    return render_template ('howtouse.html')

@app.route('/contact')
def contact():
    return render_template ('contact.html')

@app.route('/branchdetails')
def branchdetials():
    code = request.args.get('code', '')
    branch = db.get_branch(int(float(code)))
    

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")
#======================Cart=====================================================

@app.route('/addtocart', methods = ['GET', 'POST'])
def addtocart():

    code = request.form.get('code', '')
    product = db.get_product(int(code))
    qty = request.form.get('Quantity', '')

    item=dict()
    item["stallid"] = product["stallid"]
    item["code"] = code
    item["qty"] = int(qty)
    item["name"] = product["name"]
    item["price"] = product["price"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/remove', methods = ['POST'])
def remove():

    code = request.form.get('code', '')
    product = db.get_product(int(code))
    qty = request.form.get('reset', '')

    item=dict()
    item["stallid"] = product["stallid"]
    item["code"] = code
    item["qty"] = int(qty)
    item["name"] = product["name"]
    item["price"] = product["price"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')


@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/updatecart' , methods = ['POST'])
def updatecart():
    qty_all = request.form.getlist('qty_cart')
    price = request.form.getlist('price')
    code = request.form.getlist('code')
    name = request.form.getlist('name')
    stallid = request.form.getlist('stallid')

    for i in range(0,len(qty_all)):
        item=dict()
        item["stallid"]= stallid[i]
        item["qty"] = int(qty_all[i])
        item["price"] = int(price[i])
        item["name"] = name[i]
        item["code"] = int(code[i])
        item["subtotal"] = item["price"]*item["qty"]

        if(session.get("cart") is None):
            session["cart"]={}

        cart = session["cart"]
        cart[code[i]] = item
        session["cart"] = cart

    return redirect('/cart')

@app.route('/formsubmission', methods = ['POST'])
def form_submission():
    stype = request.form.get("stype")
    return render_template('formsubmission.html',stype=stype)



@app.route('/clearcart')
def clearcart():
    del session["cart"]
    return redirect('/cart')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return render_template('ordercomplete.html')

@app.route('/orderhistory')
def orderhistory():
    user_=session["user"]
    username=user_["username"]
    confirmed_order=om.check_user(username)

    if confirmed_order == True:
        past_orders=db.get_orders(username)

        return render_template('orderhistory.html', past_orders=past_orders)

    else:
        return render_template("noorders.html")


@app.route('/changepassword', methods = ['GET', 'POST'])
def changepassword():
#    if request.method == "POST":
    oldpassword = request.form.get("oldpass")
    newpassword1 = request.form.get("newpass1")
    newpassword2 = request.form.get("newpass2")

    print("oldpass")
    print("newpass1")
    print("newpass2")
    user = session["user"]
    username = user["username"]

    password = db.get_password(username)

    if oldpassword == password and newpassword1 == newpassword2:
        db.change_db(username, newpassword1)
        change_error= "Password has been updated"
        return render_template("changepassword.html", change_error=change_error)
        print (customer) 
        print (newpassword)

    elif oldpassword != password:
        change_error = "Wrong current Password"
        return render_template("changepassword.html", change_error=change_error)

    else:
        change_error = "New Passwords do not Match"
        return render_template("changepassword.html", change_error=change_error)

    return render_template('changepassword.html')