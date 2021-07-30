"""
########################################
IMPORTING STUFF
########################################
"""
from flask import Flask,render_template,request,redirect,url_for,g,session
from werkzeug.security import generate_password_hash, \
     check_password_hash
import sqlite3
from datetime import datetime
import pytz
from pytz import timezone
import os
import requests
from flask_cachebuster import CacheBuster
"""
########################################
########################################
"""






"""
########################################
CONFIGURING APP
########################################
"""
app = Flask(__name__,template_folder = 'Templates',static_folder='Static')
app.config['SECRET_KEY'] = "@\xec\xf7\t6\xe9mVc8\x1a\xad\xa2\xf2``TT\xb1SU\xf8\x14W"
ind=timezone('Asia/Kolkata')
config = { 'extensions': ['.js', '.css', '.csv'], 'hash_size': 5 }
cache_buster = CacheBuster(config=config)
cache_buster.init_app(app)






""""
########################################
CONNECTION TO DATABASE (FUNCTIONS)
########################################
"""
def connect_db():
    return sqlite3.connect('users.db')


@app.before_request
def before_request():
    g.db = connect_db()


"""
########################################
########################################
"""









'''
########################################
CLASSES
########################################
'''
class User:
    def __init__(self,id,name,password,email,phone,address,s_id,ans):
        self.id=id
        self.name=name
        self.password=password
        self.email=email
        self.phone=phone
        self.address=address
        self.s_id=s_id
        self.ans=ans


class Product:
    def __init__(self,id,name,price,ptype_id,stock):
        self.id=id
        self.name=name
        self.price=price
        self.ptype_id=ptype_id
        self.stock=stock
    def __repr__(self):
        return '<Product %r>' %self.id

class Order:
    def __init__(self,id,uid,cart_id,o_total,date,status_id):
        self.id=id
        self.uid=uid
        self.cart_id=cart_id
        self.o_total=o_total
        self.date=date
        self.status_id=status_id


class Cart_item:
    def __init__(self,cart_id,p_id,quantity,p_total):
        self.cart_id=cart_id
        self.p_id=p_id
        self.quantity=quantity
        self.p_total=p_total
"""
########################################
########################################
"""



"""
########################################
END OF CLASSES CREATION
########################################
"""













"""
########################################
FUNCTIONS
########################################
"""










"""
########################################
SOME FUNCTIONS TO RETURN EMPTY OBJECTS
########################################
"""

def EmptyUser():
    return User(None,None,None,None,None,None,None,None).__dict__

def EmptyProduct():
    return Product(None,None,None,None,None).__dict__

def EmptyOrder():
    return Order(None,None,None,None,None,None).__dict__

def EmptyCart():
    return Cart_item(None,None,None,None).__dict__

"""
########################################
########################################
"""










"""
########################################
FUNCTION TO RETURN DETAILS OF SESSION USER IF LOGGED IN
########################################
"""
def CurrentUser():
    try:
        if session['User']:
            return session['User']
    except:
        return EmptyUser()
"""
########################################
########################################
"""










"""
########################################
FUNCTION TO RETURN THE PRODUCT TYPE VALUES FROM DATABASE
########################################
"""
def ptype():
    g.db = connect_db()
    try:
        cursor = g.db.execute('SELECT value FROM Ptype;')
        ptype=cursor.fetchall()
        g.db.commit()
        g.db.close()
        return ptype
    except:
        g.db.rollback()
        g.db.close()
        return("Exception in ptype function")
"""
########################################
########################################
"""













"""
########################################
FUNCTION TO RETURN THE SECRET QUESTIONS
########################################
"""
def questions():
    g.db = connect_db()
    try:
        cursor = g.db.execute('SELECT id,value FROM Questions;')
        s_questions=cursor.fetchall()
        g.db.commit()
        g.db.close()
        return s_questions
    except:
        g.db.rollback()
        g.db.close()
        return("Exception in questions function")
"""
########################################
########################################
"""








"""
########################################
FUNCTION TO RETURN CURRENT CART ITEMS OF THE SESSION USER
########################################
"""
def CurrentCart_items():
    g.db = connect_db()
    try:
        cursor = g.db.execute('SELECT cart_id,p_id,quantity,p_total FROM Cart_Items WHERE cart_id=(SELECT id FROM Cart WHERE (uid=? AND status_id=1));',[CurrentUser()['id']])
        cart_items=cursor.fetchall()
        g.db.commit()
        g.db.close()
        return cart_items
    except:
        g.db.rollback()
        g.db.close()
        return EmptyCart()
"""
########################################
########################################
"""








"""
########################################
FUNCTION TO RETURN THE CART ID OF THE SESSION USER[JUST THE CART ID,NO DETAILS,IGNORE THE NAME:)].
IF NO CART IS PRESENT,A NEW CART IS CREATED AND RETURNED.
########################################
"""
def CurrentCart_details():
    g.db = connect_db()
    try:
        cursor = g.db.execute('SELECT id FROM Cart WHERE (uid=? AND status_id=1);',[CurrentUser()['id']])
        cart_id=cursor.fetchall()
        if(len(cart_id)==0):
            g.db.execute("INSERT INTO Cart (uid,status_id) VALUES(?,1);",[CurrentUser()['id']])
            cursor = g.db.execute('SELECT id FROM Cart WHERE (uid=? AND status_id=1);',[CurrentUser()['id']])
            cart_id=cursor.fetchall()
        g.db.commit()
        return cart_id
    except:
        g.db.rollback()
        g.db.close()
        return ("No User Logged in!")
"""
########################################
########################################
"""








"""
########################################
FUNCTION TO RETURN THE DETAILS OF A PRODUCT(input parameter is the product id) IN THE CART OF THE SESSION USER
########################################
"""
def getpincurrentcart(id):
    g.db = connect_db()
    try:
        cursor = g.db.execute('SELECT cart_id,p_id,quantity,p_total FROM Cart_Items WHERE cart_id=(SELECT id FROM Cart WHERE (uid=? AND status_id=?)) AND p_id=?;',[(CurrentUser()['id']),1,id])
        cart_items=cursor.fetchall()
        g.db.commit()
        g.db.close()
        return cart_items
    except:
        g.db.rollback()
        g.db.close()
        return EmptyCart()
"""
########################################
########################################
"""









"""
########################################
FUNCTION TO RETURN THE TOTAL OF CART OF SESSION USER
########################################
"""
def CurrentCart_total():
    g.db = connect_db()
    try:
        if session['User']:
            args=[int(CurrentCart_details()[0][0])]
            cursor = g.db.execute('SELECT TOTAL(p_total) FROM Cart_Items WHERE cart_id=?;',args)
            total = int(cursor.fetchall()[0][0])
            g.db.commit()
            g.db.close()
            return total
        else:
            return ("Session User should not be None")
    except:
        g.db.rollback()
        g.db.close()
        return("Exception during calculation of cart total")
"""
########################################
########################################
"""









"""
########################################
FUNCTION TO PLACE ORDER(CHANGE STATUS OF A CART TO ORDERED AND UPDATING ORDERS TABLE)
########################################
"""
def CreateOrder(cart_id):
    g.db = connect_db()
    cursor = g.db.execute('SELECT status_id FROM Cart WHERE id=? and uid=?;',[cart_id,CurrentUser()['id']])
    statusofcart=cursor.fetchall()[0][0]
    g.db.commit()
    g.db.close()
    if statusofcart!=1:
        return(1)
    else:
        args=[int(CurrentUser()['id']),cart_id,CurrentCart_total(),datetime.now(ind).strftime("%d-%m-%Y %H:%M:%S"),2]
        g.db = connect_db()
        g.db.execute('INSERT INTO Orders(uid,cart_id,total,order_date,status_id) VALUES (?,?,?,?,?)',args)
        g.db.commit()
        g.db.close()
        g.db = connect_db()
        args=[cart_id]
        g.db.execute('UPDATE Cart SET status_id=2 WHERE id=?',args)
        g.db.commit()
        g.db.close()
        return(0)
"""
########################################
########################################
"""













"""
########################################
FUNCTION TO CANCEL AN ORDER AND RESTOCKING PRODUCTS
########################################
"""
def changestatusofordertocancelled(id):
    try:
        g.db = connect_db()
        cursor = g.db.execute('SELECT status_id FROM Orders WHERE id=? and uid=?;',[id,CurrentUser()['id']])
        status_id=cursor.fetchall()[0][0]
        g.db.commit()
        g.db.close()
        if status_id!=3:
            g.db = connect_db()
            g.db.execute('Update Orders SET status_id=3 WHERE id=? and uid=?;',[id,CurrentUser()['id']])
            g.db.commit()
            g.db.close()
            g.db = connect_db()
            cursor = g.db.execute('SELECT cart_id FROM Orders WHERE id=? and uid=?;',[id,CurrentUser()['id']])
            cart_id=cursor.fetchall()[0][0]
            g.db.commit()
            g.db.close()
            g.db = connect_db()
            args=[cart_id]
            g.db.execute('UPDATE Cart SET status_id=3 WHERE id=?',args)
            g.db.commit()
            g.db.close()
            g.db = connect_db()
            cursor=g.db.execute('Select p_id,quantity FROM Cart_Items WHERE cart_id=?',args)
            pofcart=cursor.fetchall()
            g.db.commit()
            g.db.close()
            for i in pofcart:
                quantity=i[1]
                pid=i[0]
                args=[quantity,pid]
                g.db = connect_db()
                g.db.execute('UPDATE Products SET Stock=Stock+? WHERE id=?',args)
                g.db.commit()
                g.db.close()
        return 0
    except:
        return 1
"""
########################################
########################################
"""















"""
########################################
FUNCTION TO RETURN ORDER ITEMS GIVEN THE ORDER ID
########################################
"""
def vieworderitems(id):
    try:
        g.db = connect_db()
        cursor=g.db.execute('SELECT cart_id FROM Orders WHERE id=? and uid=?;',[id,CurrentUser()['id']])
        cart_id=cursor.fetchall()[0][0]
        g.db.commit()
        g.db.close()
        g.db = connect_db()
        cursor=g.db.execute('SELECT cart_id,p_id,quantity,p_total FROM Cart_Items WHERE cart_id=?;',[cart_id])
        ordered_items=cursor.fetchall()
        g.db.commit()
        g.db.close()
        return ordered_items
    except:
        return("Exception during viewing the order items")
"""
########################################
END OF FUNCTIONS
########################################
"""














"""
########################################
ROUTES
########################################
"""













'''
########################################
HOME PAGE VIEW
########################################
'''
@app.route('/')
def home():
    return render_template('index.html',currentuser=CurrentUser(),successmsg="")

'''
##########################################
##########################################
'''







'''
#########################################
PROFILE PAGE VIEW
#########################################
'''
@app.route('/profile')
def profilepage():
    try:
        if session['User']:
           return render_template('profile.html',currentuser=CurrentUser())
        else :
           return render_template('login.html',msg="Log In to Access this Page!",currentuser=CurrentUser())
    except:
        return render_template('login.html',msg="Log In to Acces this Page!",currentuser=CurrentUser())
'''
##########################################
##########################################
'''






'''
###########################################
LOGIN PAGE VIEW
###########################################
'''
@app.route('/login',methods=['GET'])
def login():
    try:
        if session['User']:
            return render_template('index.html',msg="Already Logged in as "+CurrentUser().name+"!! Please Logout First!")
    except :
        return render_template('login.html',currentuser=CurrentUser())
'''
##########################################
##########################################
'''














'''
###########################################
LOGGING IN
###########################################
'''
@app.route('/login',methods=['POST'])
def loginuser():
    g.db = connect_db()
    try:
        if session['User'] :
            return render_template('index.html',msg="Already Signed in as "+CurrentUser().name+"!! Please Logout First!")
    except :
        cursor = g.db.execute('SELECT password FROM Users WHERE email = ?',[request.form['email']])
        passwordh = cursor.fetchall()
        try:
            if(check_password_hash(passwordh[0][0],request.form['password'])):
                uid = g.db.execute('SELECT id FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                name= g.db.execute('SELECT name FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                email=request.form['email']
                phone=g.db.execute('SELECT phone FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                address=g.db.execute('SELECT address FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                session['User']=User(uid[0][0],name[0][0],None,email,phone[0][0],address[0][0],None,None).__dict__
                g.db.commit()
                g.db.close()
                return render_template('index.html',currentuser=CurrentUser(),successmsg="Welcome,"+CurrentUser()['name']+".")
            else:
                g.db.rollback()
                g.db.close()
            return render_template('login.html',currentuser=CurrentUser(),msg="Incorrect Email or Password! Please Register if not done.")
        except :
            return render_template('login.html',currentuser=CurrentUser(),msg="Invalid Email or Password!Please Register if not done.")
'''
##########################################
##########################################
'''













'''
########################################
REGISTER PAGE VIEW
########################################
'''
@app.route('/signup', methods=['GET'])
def signuppage():
    try:
        if session['User']:
            return render_template('login.html',msg="Already Logged in as "+CurrentUser()['name']+"!! Please Logout First!")
    except :
        return render_template('signup.html',currentuser=CurrentUser(),questions=questions())
'''
########################################
########################################
'''












'''
########################################
REGISTERING NEW USER
########################################
'''
@app.route('/signup',methods=['POST'])
def newuser():
    g.db = connect_db()
    try:
        if session['User']:
            return render_template('login.html',msg="Already Logged in as "+CurrentUser()['name']+"!! Please Logout First!")
    except :
        init_check = g.db.execute('SELECT COUNT(*) FROM Users WHERE email = ?',[request.form['email']]).fetchall()
        if init_check[0][0] == 0:
            init_check=g.db.execute('SELECT COUNT(*) FROM Users WHERE phone = ?',[request.form['phone']]).fetchall()
            if init_check[0][0]==0:
                passwordh = generate_password_hash(request.form['password'])
                new_user=User(id=None,name=request.form['name'],password=passwordh,email=request.form['email'],phone=request.form['phone'],address=request.form['address'],s_id=request.form['question'],ans=request.form['answer'].lower())
                g.db.execute('INSERT INTO Users(name,password,email,phone,address,s_id,ans) VALUES (?,?,?,?,?,?,?)',[new_user.name,passwordh,new_user.email,new_user.phone,new_user.address,new_user.s_id,new_user.ans])
                g.db.commit()
                g.db.close()
                return render_template('login.html',successmsg="Account Successfully Created! Please Login.",currentuser=CurrentUser())
            else :
                g.db.rollback()
                g.db.close()
                return render_template('login.html',msg="An account with that phone number already exists.Please Login.",currentuser=CurrentUser())
        else:
            return render_template('login.html',msg="An account with that email already exists.Please Login",currentuser=CurrentUser())
'''
########################################
########################################
'''









'''
########################################
PRODUCTS PAGE VIEW
########################################
'''
@app.route('/products',  methods=['GET'])
def products():
    g.db = connect_db()
    cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products;')
    products = cursor.fetchall()
    g.db.commit()
    g.db.close()
    return render_template('products.html',currentuser=CurrentUser(),products=products,ptype=ptype())
'''
#########################################
#########################################
'''













'''
#########################################
PRODUCTS SEARCH OPERATION
#########################################
'''
@app.route('/products',methods=['POST'])
def productsearch():
    g.db = connect_db()
    if "search" in request.form:
        try:
            stat='SELECT id,name,ptype_id,price,stock FROM Products WHERE name LIKE ? ;'
            arg=["%"+[request.form['search_name']][0]+"%"]
            cursor = g.db.execute(stat,arg)
            products=cursor.fetchall()
            stat='SELECT id,name,ptype_id,price,stock FROM Products WHERE ptype_id IN (SELECT id FROM Ptype WHERE value LIKE ? );'
            cursor = g.db.execute(stat,arg)
            products=products+cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template('products.html',currentuser=CurrentUser(),products=products,ptype=ptype())
        except:
            return("Exception during Search")
    else: return("Wrong call of POST Method")
'''
#########################################
#########################################
'''










'''
##########################################
ADDING TO CART PAGE VIEW
#########################################
'''
@app.route('/addtocart/<int:pid>',methods=['GET'])
def addtocartview(pid):
    try:
        if session['User'] :
            try:
                pincart=getpincurrentcart(pid)
                g.db = connect_db()
                cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products WHERE id=?;',[pid])
                product = cursor.fetchall()
                g.db.commit()
                g.db.close()
                return render_template('addtocart.html',currentuser=CurrentUser(),item=pincart,ptype=ptype(),product=product,msg="")
            except:
                g.db = connect_db()
                g.db.rollback()
                g.db.close()
                return ("Exception occured")
        else :
            return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to Add to Cart!")
    except:
       return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to Add to Cart!")
'''
#########################################
#########################################
'''






'''
##########################################
ADDING TO CART OPERATION
#########################################
'''
@app.route('/addtocart/<int:pid>',methods=['POST'])
def addtocart(pid):
    try:
        pincart=getpincurrentcart(pid)
        g.db = connect_db()
        cursor = g.db.execute('SELECT price FROM Products WHERE id=?;',[pid])
        price = cursor.fetchall()
        ptotal=int(request.form['quantity'])*int(price[0][0])
        cursor = g.db.execute('SELECT stock FROM Products WHERE id=?;',[pid])
        stock = cursor.fetchall()
        if len(pincart)!=0:
            realstock=stock[0][0]+int(pincart[0][2])
        else:
            realstock=stock[0][0]
        g.db.commit()
        g.db.close()
    except:
        g.db = connect_db()
        g.db.rollback()
        g.db.close()
        return("Exception occured while executing select price and stock")
    if int(request.form['quantity'])>realstock :
        try:
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products WHERE id=?;',[pid])
            product = cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template('addtocart.html',currentuser=CurrentUser(),msg="Quantity selected is higher than the available stock,Sorry!",item=pincart,ptype=ptype(),product=product)
        except:
            g.db = connect_db()
            g.db.rollback()
            g.db.close()
            return("Exception occured while refreshing due to higher quantity than stock")
    if int(request.form['quantity'])<=0 :
        try:
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products WHERE id=?;',[pid])
            product = cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template('addtocart.html',currentuser=CurrentUser(),msg="Please Enter Quantity Higher than 0!",item=pincart,ptype=ptype(),product=product)
        except:
            g.db = connect_db()
            g.db.rollback()
            g.db.close()
            return("Exception occured while refreshing due to negative quantity/0")
    if len(pincart)==0 :
        try:
            g.db = connect_db()
            args=[int(CurrentCart_details()[0][0]),pid,int(request.form['quantity']),ptotal]
            g.db.execute('INSERT INTO Cart_Items(cart_id,p_id,quantity,p_total) VALUES (?,?,?,?)',args)
            g.db.commit()
            g.db.close()
            newstock=stock[0][0]-int(request.form['quantity'])
            g.db = connect_db()
            g.db.execute('Update Products SET stock=? WHERE id=?',[newstock,pid])
            g.db.commit()
            g.db.close()
        except:
            g.db = connect_db()
            g.db.rollback()
            g.db.close()
            return("Exception during Inserting to database")
    else :
        try:
            g.db = connect_db()
            args=[int(request.form['quantity']),int(CurrentCart_details()[0][0]),pid]
            g.db.execute("UPDATE Cart_Items SET quantity=? WHERE cart_id = ? and p_id=?",args)
            g.db.commit()
            ptotal=int(request.form['quantity'])*int(price[0][0])
            args=[ptotal,int(CurrentCart_details()[0][0]),pid]
            g.db.execute("UPDATE Cart_Items SET p_total=? WHERE cart_id = ? and p_id=?",args)
            newstock=realstock-int(request.form['quantity'])
            args=[newstock,pid]
            g.db.execute('Update Products SET stock=? WHERE id=?',args)
            g.db.commit()
            g.db.close()
        except:
            g.db = connect_db()
            g.db.rollback()
            g.db.close()
            return("Exception during Updating database")
    g.db = connect_db()
    cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products;')
    products = cursor.fetchall()
    g.db.commit()
    g.db.close()
    return render_template('cart.html',successmsg="Item added to cart",currentuser=CurrentUser(),cart=CurrentCart_items(),product=products,ptype=ptype(),total=CurrentCart_total())

'''
#########################################
#########################################
'''







'''
#########################################
CART VIEW
#########################################
'''
@app.route('/cart',methods=['GET'])
def viewcart():
    try:
        if session['User']:
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products;')
            products = cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template('cart.html',currentuser=CurrentUser(),cart=CurrentCart_items(),product=products,ptype=ptype(),total=CurrentCart_total())
        else:
            return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to View Cart!")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to View Cart!")

'''
########################################
########################################
'''






'''
########################################
DELETING FROM CART AND RESTOCKING PRODUCTS
########################################
'''
@app.route('/addtocart/<int:pid>/delete/<int:cart_id>',methods=['GET'])
def deleteitemfromcart(pid,cart_id):
    try:
        if session['User']:
            args=[pid,cart_id]
            quantity=int(getpincurrentcart(pid)[0][2])
            g.db = connect_db()
            g.db.execute('DELETE FROM Cart_Items WHERE p_id=? AND  cart_id=?;',args)
            g.db.commit()
            args=[quantity,pid]
            g.db = connect_db()
            g.db.execute('UPDATE Products SET Stock=Stock+? WHERE id=?',args)
            g.db.commit()
            g.db.close()
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products;')
            products = cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template('cart.html',successmsg="Item deleted from cart",currentuser=CurrentUser(),cart=CurrentCart_items(),product=products,ptype=ptype(),total=CurrentCart_total())
    except:
        g.db = connect_db()
        g.db.rollback()
        g.db.close()
        return("Exception occured during deletion")
'''
########################################
########################################
'''









'''
########################################
CONFIRMATION BEFORE ORDER VIEW
########################################
'''
@app.route('/confirmorder',methods=['GET'])
def confirmorder():
    try:
        if session['User']:
            return render_template('confirmorder.html',currentuser=CurrentUser(),cart_id=int(CurrentCart_items()[0][0]))
        else:
            return("Session user cannot be None")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to Confirm any order!")

'''
#######################################
#######################################
'''








'''
#########################################
PLACING ORDER
#########################################
'''
@app.route('/confirmorder/<int:cart_id>',methods=['GET'])
def placeorder(cart_id):
    try:
        if session['User']:
            a=CreateOrder(cart_id)
            if a==1:
                return("Cart not found.Either the cart is already ordered or doesn't belong to you!")
            else:
                g.db = connect_db()
                cursor = g.db.execute('SELECT id,uid,cart_id,total,order_date,status_id FROM Orders WHERE uid=?;',[CurrentUser()['id']])
                orders = cursor.fetchall()
                g.db.commit()
                g.db.close()
                return render_template("orders.html",orders=orders,successmsg="Order Successfully Placed!",currentuser=CurrentUser())
        else:
            return("Session User shouldn't be None")
    except:
        return("Exception during Placing Order")

'''
########################################
########################################
'''










'''
#########################################
ORDER PAGE VIEW
#########################################
'''
@app.route('/orders',methods=['GET'])
def orderspage():
    try:
        if session['User']:
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,uid,cart_id,total,order_date,status_id FROM Orders WHERE uid=?;',[CurrentUser()['id']])
            orders = cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template("orders.html",orders=orders,successmsg="",currentuser=CurrentUser())
        else:
            return("Session User shouldn't be None")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to view your orders!")

'''
########################################
########################################
'''













'''
#########################################
CANCEL ORDER
#########################################
'''
@app.route('/cancelorder/<int:id>',methods=['GET'])
def cancelorder(id):
    try:
        if session['User']:
            a=changestatusofordertocancelled(id)
            if a==1:
                return("Failure occured while changing status of order")
            else:
                g.db = connect_db()
                cursor = g.db.execute('SELECT id,uid,cart_id,total,order_date,status_id FROM Orders WHERE uid=?;',[CurrentUser()['id']])
                orders = cursor.fetchall()
                g.db.commit()
                g.db.close()
                return render_template("orders.html",orders=orders,successmsg="Order Cancelled!",currentuser=CurrentUser())
        else:
            return("Session User cannot be None!")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to cancel your order!")
'''
########################################
########################################
'''



'''
#########################################
VIEW ORDER DETAILS
#########################################
'''
@app.route('/vieworder/<int:id>',methods=['GET'])
def vieworderdetails(id):
    try:
        if session['User']:
            ordered_items=vieworderitems(id)
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,name,ptype_id,price,stock FROM Products;')
            products = cursor.fetchall()
            g.db.commit()
            g.db.close()
            g.db = connect_db()
            cursor = g.db.execute('SELECT id,total,order_date,status_id FROM Orders WHERE id=? AND uid=?;',[id,CurrentUser()['id']])
            order = cursor.fetchall()
            g.db.commit()
            g.db.close()
            return render_template("vieworderdetails.html",order=order,currentuser=CurrentUser(),products=products,ordered_items=ordered_items,ptype=ptype())
        else:
            return("Session User cannot be None!")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to cancel your order!")
'''
########################################
########################################
'''







'''
########################################
VIEW FILLED CONTACTFORMS
########################################
'''
@app.route('/msgs')
def msgs():
    try:
        if CurrentUser()['id']==1:
            try:
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM ContactForm;')
                messages = cursor.fetchall()
                g.db.commit()
                g.db.close()
                return render_template('msgs.html',messages=messages,currentuser=CurrentUser())
            except:
                return("Unexpected Error in database.")
        else:
            return render_template(url_for(home))
    except:
        return render_template(url_for(home))





'''
########################################
DATABASE DEBUG PAGE
########################################
'''
@app.route('/debug')
def databasedebug():
    try:
        if CurrentUser()['id']==1:
            try:
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Products;')
                products = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Users;')
                users = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Cart;')
                carts = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Cart_items;')
                cart_items = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Status;')
                status = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Orders;')
                orders = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Ptype;')
                ptype = cursor.fetchall()
                g.db.commit()
                g.db.close()
                g.db = connect_db()
                cursor = g.db.execute('SELECT * FROM Questions;')
                questions = cursor.fetchall()
                g.db.commit()
                g.db.close()
                return render_template('debug.html',users=users,questions=questions,products=products,ptype=ptype,orders=orders,carts=carts,cart_items=cart_items,status=status,currentuser=CurrentUser())
            except:
                return("Unexpected Error in database.")
        else:
            return render_template(url_for(home))
    except:
        return render_template(url_for(home))
'''
########################################
########################################
'''








'''
########################################
EDIT PROFILE PAGE VIEW
########################################
'''
@app.route('/editprofile',methods=['GET'])
def editprofilepage():
    try:
        if session['User']:
            return render_template('editprofile.html',currentuser=CurrentUser(),successmsg="",msg="")
        else:
            return('Session User cannot be None!')
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to edit your profile!")
'''
########################################
########################################
'''








'''
########################################
EDITING PROFILE
########################################
'''
@app.route('/editprofile',methods=['POST'])
def editprofile():
    try:
        if session['User']:
            g.db = connect_db()
            init_check = g.db.execute('SELECT COUNT(*) FROM Users WHERE email = ?',[request.form['email']]).fetchall()
            g.db.commit()
            g.db.close()
            if init_check[0][0] <= 1:
                g.db = connect_db()
                init_check=g.db.execute('SELECT COUNT(*) FROM Users WHERE phone = ?',[request.form['phone']]).fetchall()
                g.db.commit()
                g.db.close()
                if init_check[0][0]<=1:
                    new_user=User(id=None,name=request.form['name'],password=None,email=request.form['email'],phone=request.form['phone'],address=request.form['address'],s_id=None,ans=None)
                    g.db = connect_db()
                    g.db.execute('UPDATE Users SET name=?,email=?,phone=?,address=? WHERE id=?;',[new_user.name,new_user.email,new_user.phone,new_user.address,CurrentUser()['id']])
                    g.db.commit()
                    g.db.close()
                    session.pop('User',None)
                    g.db = connect_db()
                    uid = g.db.execute('SELECT id FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                    name= g.db.execute('SELECT name FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                    email=request.form['email']
                    phone=g.db.execute('SELECT phone FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                    address=g.db.execute('SELECT address FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                    session['User']=User(uid[0][0],name[0][0],None,email,phone[0][0],address[0][0],None,None).__dict__
                    g.db.commit()
                    g.db.close()
                    return render_template('profile.html',successmsg="Account Updated Successfully!",msg="",currentuser=CurrentUser())
                else :
                    g.db.rollback()
                    g.db.close()
                    return render_template('editprofile.html',successmsg="",msg="Another account with that phone number already exists",currentuser=CurrentUser())
            else:
                return render_template('editprofile.html',successmsg="",msg="Another account with that email already exists",currentuser=CurrentUser())
        else:
            return("Session User cannot be None!")
    except:
        return("Exception During Editing Profile")


'''
########################################
########################################
'''







'''
#######################################
CONFIRM DELETE ACCOUNT
#######################################
'''
@app.route('/deleteprofile',methods=['GET'])
def deleteprofilepage():
    try:
        if session['User']:
            return render_template('confirmdeleteprofile.html',currentuser=CurrentUser(),msg="")
        else:
            return ("Session User cannot be None!")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to delete your profile!")

'''
########################################
########################################
'''










'''
#######################################
DELETING ACCOUNT[CANCELLING USER'S ORDERS,RESTOCKING PRODUCTS,DELETING USER'S ORDERS,CARTS AND ACCOUNT INFO]
#######################################
'''
@app.route('/deleteprofile',methods=['POST'])
def deleteprofile():
    try:
        if session['User']:
                g.db = connect_db()
                cursor = g.db.execute('SELECT password FROM Users WHERE email = ?',[CurrentUser()['email']])
                passwordh = cursor.fetchall()
                g.db.commit()
                g.db.close()
                if(check_password_hash(passwordh[0][0],request.form['password'])):
                    g.db = connect_db()
                    cursor=g.db.execute('SELECT id FROM Orders WHERE uid = ?',[CurrentUser()['id']])
                    order_ids=cursor.fetchall()
                    g.db.commit()
                    g.db.close()
                    for i in order_ids:
                        a=changestatusofordertocancelled(i[0])
                        if a==1:
                            return("Failure occured while changing status of order")
                    current_cart=CurrentCart_items()
                    for i in current_cart:
                        args=[i[1],i[0]]
                        quantity=int(getpincurrentcart(i[1])[0][2])
                        g.db = connect_db()
                        g.db.execute('DELETE FROM Cart_Items WHERE p_id=? AND  cart_id=?;',args)
                        g.db.commit()
                        args=[quantity,i[1]]
                        g.db = connect_db()
                        g.db.execute('UPDATE Products SET Stock=Stock+? WHERE id=?',args)
                        g.db.commit()
                        g.db.close()
                    g.db = connect_db()
                    cursor=g.db.execute('SELECT id FROM Cart WHERE uid=? ;',[CurrentUser()['id']])
                    allcarts=cursor.fetchall()
                    g.db.commit()
                    g.db.close()
                    for i in allcarts:
                        g.db=connect_db()
                        g.db.execute('DELETE FROM Cart_Items WHERE cart_id=?;',[i[0]])
                        g.db.commit()
                        g.db.close()
                    g.db = connect_db()
                    g.db.execute('DELETE FROM Cart WHERE uid=?;',[CurrentUser()['id']])
                    g.db.commit()
                    g.db.close()
                    g.db = connect_db()
                    g.db.execute('DELETE FROM Orders WHERE uid=?;',[CurrentUser()['id']])
                    g.db.commit()
                    g.db.close()
                    g.db = connect_db()
                    g.db.execute('DELETE FROM Users WHERE id=?;',[CurrentUser()['id']])
                    g.db.commit()
                    g.db.close()
                    session.pop('User',None)
                    return render_template('index.html',currentuser=CurrentUser(),successmsg="Account deleted Successfully!")
                else:
                    g.db = connect_db()
                    g.db.rollback()
                    g.db.close()
                    return render_template('confirmdeleteprofile.html',currentuser=CurrentUser(),msg="Incorrect Password!")
        else:
            return("Session User cannot be None!")
    except:
        return("Exception during deleting account!")
'''
########################################
########################################
'''













'''
#######################################
RESET PASSWORD VIEW
#######################################
'''
@app.route('/resetpassword',methods=['GET'])
def resetpasswordview():
    try:
        if session['User']:
            return render_template('resetpassword.html',currentuser=CurrentUser(),successmsg="")
        else:
             return("Session User Cannot be None!")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to reset your password!")
'''
########################################
########################################
'''














'''
#######################################
RESET PASSWORD Operation
#######################################
'''
@app.route('/resetpassword',methods=['POST'])
def resetpassword():
    try:
        if session['User']:
                    passwordh = generate_password_hash(request.form['password'])
                    g.db = connect_db()
                    g.db.execute('UPDATE Users SET password=? WHERE id=?;',[passwordh,CurrentUser()['id']])
                    g.db.commit()
                    g.db.close()
                    return render_template('profile.html',successmsg="Password Updated Successfully!",msg="",currentuser=CurrentUser())
        else:
             return("Session User Cannot be None!")
    except:
        return render_template('login.html',currentuser=CurrentUser(),msg="Please Login to reset your password!")
'''
########################################
########################################
'''















'''
#######################################
FORGOT PASSWORD PAGE VIEW
#######################################
'''
@app.route('/forgotpassword',methods=['GET'])
def forgotpasswordview():
    return render_template('forgotpassword.html',currentuser=CurrentUser(),questions=questions(),msg="")
'''
########################################
########################################
'''















'''
#######################################
FORGOT PASSWORD PAGE OPERATION
#######################################
'''
@app.route('/forgotpassword',methods=['POST'])
def forgotpassword():
    g.db = connect_db()
    try:
        if session['User'] :
            return render_template('login.html',msg="Already Signed in as "+CurrentUser().name+"!! Please Logout First!")
    except :
        cursor = g.db.execute('SELECT s_id,ans FROM Users WHERE email = ?',[request.form['email']])
        auth = cursor.fetchall()
        try:
            if auth[0][0]==int(request.form['question']) and auth[0][1].lower()==str(request.form['answer']).lower():
                uid = g.db.execute('SELECT id FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                name= g.db.execute('SELECT name FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                email=request.form['email']
                phone=g.db.execute('SELECT phone FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                address=g.db.execute('SELECT address FROM Users WHERE email = ?',[request.form['email']]).fetchall()
                session['User']=User(uid[0][0],name[0][0],None,email,phone[0][0],address[0][0],None,None).__dict__
                g.db.commit()
                g.db.close()
                return render_template('resetpassword.html',currentuser=CurrentUser(),successmsg="Welcome "+CurrentUser()['name']+". Please choose a new password.")
            else:
                g.db.rollback()
                g.db.close()
                return render_template('forgotpassword.html',currentuser=CurrentUser(),msg="Incorrect Secret Question or answer!",questions=questions())
        except :
            return render_template('forgotpassword.html',currentuser=CurrentUser(),msg="Invalid Email! Please Register if not done.",questions=questions())
'''
########################################
########################################
'''










'''
#######################################
ABOUT PAGE VIEW
#######################################
'''
@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html',currentuser=CurrentUser(),successmsg="")
'''
########################################
########################################
'''











'''
#######################################
CONTACT US FORM SUBMISSION
#######################################
'''
@app.route('/about',methods=['POST'])
def contactusformsubmit():
    g.db = connect_db()
    name=request.form['name']
    message=request.form['message']
    uid=0
    try:
        if session['User']:
            uid=CurrentUser()['id']
    except:
        pass
    g.db.execute('INSERT INTO ContactForm(name,msg,uid) VALUES (?,?,?)',[name,message,uid])
    g.db.commit()
    g.db.close()
    return render_template('about.html',currentuser=CurrentUser(),successmsg="Thanks for Contacting Us,"+name)
'''
########################################
########################################
'''






'''
#######################################
LOGOUT
#######################################
'''
@app.route('/logout')
def logout():
    try:
        if session['User']:
            a=CurrentUser()['name']
            session.pop('User',None)
            return render_template('index.html',currentuser=CurrentUser(),successmsg="Thank you for shopping,"+a+"!")
        else:
            return render_template('login.html',msg="Please Log in first!",currentuser=CurrentUser())
    except:
        return render_template('login.html',msg="Please Log in first!",currentuser=CurrentUser())

'''
########################################
########################################
'''












'''
########################################
PORT CREATION,TABLE CREATION,INITIALIZATION OF DATABASE AND HOSTING
########################################
'''

if __name__ == '__main__':
    with app.app_context():
        before_request()
        '''
        try:
                g.db.execute("DROP TABLE IF EXISTS Users;")
                g.db.execute("DROP TABLE IF EXISTS Orders;")
                g.db.execute("DROP TABLE IF EXISTS Cart_Items;")
                g.db.execute("DROP TABLE IF EXISTS Cart;")
                g.db.execute("DROP TABLE IF EXISTS Products;")
                g.db.execute("DROP TABLE IF EXISTS Ptype;")
                g.db.execute("DROP TABLE IF EXISTS Status;")
                g.db.execute("DROP TABLE IF EXISTS Questions;")
                g.db.execute("CREATE TABLE IF NOT EXISTS Questions(id integer PRIMARY KEY,value text NOT NULL);")
                g.db.execute("CREATE TABLE IF NOT EXISTS Users (id integer PRIMARY KEY,name text NOT NULL,email text NOT NULL,phone numeric NOT NULL,address text NOT NULL,password text NOT NULL,s_id integer NOT NULL,ans text NOT NULL,FOREIGN KEY(s_id) REFERENCES Questions(id));")
                g.db.execute("CREATE TABLE IF NOT EXISTS Ptype (id integer PRIMARY KEY,value text NOT NULL);")
                g.db.execute("CREATE TABLE IF NOT EXISTS Status (id integer PRIMARY KEY,value text NOT NULL);")
                g.db.execute("CREATE TABLE IF NOT EXISTS Products (id integer PRIMARY KEY,name text NOT NULL,price integer NOT NULL,ptype_id integer NOT NULL,stock integer NOT NULL,FOREIGN KEY (ptype_id) REFERENCES Ptype (id) ON DELETE CASCADE);")
                g.db.execute("CREATE TABLE IF NOT EXISTS Cart (id integer NOT NULL PRIMARY KEY,uid integer NOT NULL,status_id integer NOT NULL,FOREIGN KEY (uid) REFERENCES Users (id) ON DELETE CASCADE,FOREIGN KEY (status_id) REFERENCES Status (id));")
                g.db.execute("CREATE TABLE IF NOT EXISTS Cart_Items (sl integer NOT NULL PRIMARY KEY,cart_id integer NOT NULL,p_id integer NOT NULL,quantity integer NOT NULL,p_total integer NOT NULL,FOREIGN KEY (p_id) REFERENCES Products (id) ON DELETE CASCADE,FOREIGN KEY (cart_id) REFERENCES Cart (id) ON DELETE CASCADE);")
                g.db.execute("CREATE TABLE IF NOT EXISTS Orders (id integer PRIMARY KEY,uid integer NOT NULL,cart_id integer NOT NULL,total integer NOT NULL,order_date text NOT NULL,status_id integer NOT NULL,FOREIGN KEY (uid) REFERENCES Users (id) ON DELETE CASCADE,FOREIGN KEY (cart_id) REFERENCES Cart (id) ON DELETE CASCADE,FOREIGN KEY (status_id) REFERENCES Status (id));")
                g.db.execute("CREATE TABLE IF NOT EXISTS ContactForm(id integer PRIMARY KEY,name text NOT NULL,msg text NOT NULL,uid integer,FOREIGN KEY (uid) REFERENCES Users (id));")
                g.db.execute("CREATE PROCEDURE Clearorders @uid Integer AS Delete FROM Orders WHERE uid = @uid;")
                g.db.execute("CREATE TRIGGER ClearAccountinfo before DELETE on Users for each row EXEC Clearorders @uid=Users.id;")
                g.db.execute("INSERT INTO Questions(value) VALUES('What was your childhood nickname?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('Who was your childhood hero?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What is the name of your current crush?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What was your dream job?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What is your preferred musical genre?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What was the name of your second pet?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('Where were you born?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What time of the day were you born?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What is the name of your best friend?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What was your favorite place to visit as a child?');")
                g.db.execute("INSERT INTO Questions(value) VALUES('What is your favorite movie?');")
                g.db.execute("INSERT INTO Status(value) VALUES('Not Ordered');")
                g.db.execute("INSERT INTO Status(value) VALUES('Ordered');")
                g.db.execute("INSERT INTO Status(value) VALUES('Cancelled');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('SmartPhone');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Gaming Console');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Laptop');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Refrigerator');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Washing Machine');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Gym Equipment');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Sport Equipment');")
                g.db.execute("INSERT INTO Ptype(value) VALUES('Shoes');")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('iPhone 12',74990,1,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('iPhone 12 Pro',99990,1,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('iPhone 11',52999,1,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Samsung S20',95800,1,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Samsung M51',22999,1,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Samsung M31',16499,1,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Playstation 5',49999,2,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Playstation 4',32499,2,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Xbox One',29990,2,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Xbox Series S',34990,2,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Lenovo Ideapad',66990,3,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Macbook Pro',122900,3,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Macbook Air',74699,3,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Surface Laptop',110499,3,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Samsung 235L',23050,4,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Haier 181L',9990,4,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Samsung 192L',11790,4,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Godrej 260L',22290,4,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Whirlpool 200L',15990,4,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Panasonic 584L',59990,4,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Whirlpool 65K',13990,5,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Whirlpool 70K',9190,5,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Samsung 60K',8240,5,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Godrej 60K',12290,5,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('LG W82',19900,5,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Hex Dumbbells 7.5kg',2499,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Hex Dumbbells 10kg',5099,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Resistance Bands',799,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Battle Ropes',1199,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Treadmill',32499,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Cycling Machine',12999,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('PVC Dumbbells 5kg',999,6,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('SG Cricket Bat',1499,7,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('SS Cricket Bat',2499,7,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Nike ManU Football',2199,7,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Trek Bicycle',21999,7,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('YONEX Badminton Racquet',11900,7,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Babolat Tennis Racquet',10699,7,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Yeezy 350',25700,8,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Air Jordan 6',16595,8,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Jordan Zoom',12995,8,50);")
                g.db.execute("INSERT INTO Products (name,price,ptype_id,stock) VALUES('Balenciaga',55499,8,50);")
                g.db.commit()
                g.db.close()
        except:
                g.db.rollback()
                g.db.close()
        '''
    app.run(debug=True)

"""
##########################################
##########################################
"""