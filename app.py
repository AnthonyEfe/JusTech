from flask import Flask,request,render_template,redirect,url_for,session

from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'shop'

mysql = MySQL(app)

app.secret_key='mrkingone'

@app.route('/')                                               
def index():
    stocks = []
    hide = 'd-none'
    show = 'd-block'
    cartLen = 0
    if 'userLoggedIn' in session:
        hide = 'd-block'
        show = 'd-none'
        userId = int(session['userLoggedIn'])
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE user_id = %s", [userId])
        cart = cur.fetchall()
        cartLen = len(cart)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stocks LIMIT 6")
    stocks = cur.fetchall()
    
    #return 'This is Aptech Port Harcourt':
    return render_template('index.html', hide = hide, show = show, stocks=stocks, cartLen=cartLen)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup',methods=['POST','GET'])
def signup():
    hide = 'd-none'
    show = 'd-block'
    if 'userLoggedIn' in session:
        return redirect('/')
    if request.method == 'POST':
        details = request.form.get
        uname = details('uname')
        address = details('address')
        email = details('email')
        city = details('city')
        password = details('pass')
        userzip = details('userzip') 
        state = details('state') 
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO customers (username, address, email, city, password, state, userzip) VALUES (%s, %s, %s, %s, %s, %s, %s)''', (uname, address, email, city, password, userzip, state))
        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('signup.html', hide=hide, show=show)

@app.route('/login', methods=['POST','GET'])
def login():
    hide = 'd-none'
    show = 'd-block'
    if 'userLoggedIn' in session:
        return redirect('/')
    errormsg = "d-none"
    if request.method == 'POST':
        details = request.form.get
        email = details('email')
        password = details('pass')  
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM customers''')
        users = cur.fetchall()

        for user in users:
            if user[2] == email and user[3] == password:
                # Set login session to user id
                session["userLoggedIn"] = user[0]
                return redirect('/')
                break
            else:
                errormsg = "d-block"
        mysql.connection.commit()
        cur.close()
        
    return render_template('login.html', errormsg=errormsg, hide = hide, show = show)

@app.route('/contact')
def contact():
   return render_template('contact.html')

@app.route('/shop', methods=['POST','GET'])
def shop():
    hide = 'd-none'
    show = 'd-block'
    search = ''
    stocks = []
    searchStocks = []
    cartLen = 0
    if 'userLoggedIn' in session:
        hide = 'd-block'
        show = 'd-none'
        userId = int(session['userLoggedIn'])
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE user_id = %s", [userId])
        cart = cur.fetchall()
        cartLen = len(cart)
    if request.method == 'POST':
        details = request.form.get
        search = details('inputSearch')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stocks")
        searchStocks = cur.fetchall()
        for i in searchStocks:
            if search.lower() in i[1].lower():
                stocks.append(i)
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stocks")
        stocks = cur.fetchall()
    return render_template('shop.html', hide=hide, show=show, stocks=stocks, search=search, cartLen=cartLen)    

@app.route('/logout')
def logout():
    session.pop('userLoggedIn', None)
    return redirect('/')
#    return render_template('shop.html') 

@app.route('/cart')
def cart():
    if 'userLoggedIn' in session:
        hide = 'd-block'
        show = 'd-none'
        cartLen = 0
        subtotal = 0
        total = 0
        userId = int(session['userLoggedIn'])
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart as a JOIN stocks as b ON a.stock_id=b.stock_id WHERE user_id = %s", [userId])
        cart = cur.fetchall()
        cartLen = len(cart)
        tax = 1000 * cartLen
        for item in cart:
            subtotal += item[8]
        total = subtotal + tax
    else:
        return redirect('/')
    
    return render_template('cart.html', hide=hide, show=show,  cartLen=cartLen, cart=cart, total=total, subtotal=subtotal, tax=tax)

@app.route('/profile', methods=['POST','GET'])
def profile():
    if 'userLoggedIn' in session:
        hide = 'd-block'
        show = 'd-none'
        cartLen = 0
        userId = int(session['userLoggedIn'])
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cart WHERE user_id = %s", [userId])
        cart = cur.fetchall()
        cartLen = len(cart)
        user = []
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM customers WHERE id = %s", [userId])
        user = cur.fetchone()
        errormsg = 'd-none'
        if request.method == 'POST':
            details = request.form.get
            name = details('name')
            address = details('address')
            city = details('city')
            state = details('state')
            oldp = details('oldp')
            newp = details('newp')
            if oldp == user[3]:
                cur = mysql.connection.cursor()
                cur.execute('UPDATE customers SET username=%s, address=%s, city=%s, state=%s, password=%s WHERE id = %s', (name, address, city, state, newp, [userId]))
                mysql.connection.commit()
                cur.close()
            else:
                errormsg = 'd-block'
        
        # Get all orders
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM checkout WHERE user_id = %s", [userId])
        orders = cur.fetchall()
    else:
        return redirect('/')
    return render_template('profile.html', hide=hide,orders=orders, show=show, cartLen=cartLen, user=user, errormsg=errormsg) 

@app.route('/add-cart', methods=['POST','GET'])
def addCart():
    prevPage = ''
    if 'userLoggedIn' in session:
        if request.method == 'GET':
            details = request.args.get
            stockId = details('stockId')
            userId = int(session['userLoggedIn'])
            prevPage = details('prevPage')
            if stockId:
                cur = mysql.connection.cursor()
                cur.execute('''INSERT INTO cart (user_id, stock_id) VALUES (%s, %s)''', (userId, stockId))
                mysql.connection.commit()
                return redirect(prevPage)
        else:
            return redirect('/')
    return redirect('/')

@app.route('/remove-cart', methods=['POST','GET'])
def removeCart():
    if 'userLoggedIn' in session:
        if request.method == 'GET':
            details = request.args.get
            stockId = details('stockId')
            if stockId:
                cur = mysql.connection.cursor()
                cur.execute('''DELETE FROM cart WHERE cart_id=%s''', [stockId])
                mysql.connection.commit()
                return redirect('/cart')
        else:
            return redirect('/')
    return redirect('/')
    # return render_template('search.html')

@app.route('/checkout', methods=['POST','GET'])
def checkout():
    if 'userLoggedIn' in session:
        if request.method == 'POST':
            details = request.form.get
            item_len = details('len')
            total = details('total')
            userId = int(session['userLoggedIn'])
            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO checkout (price, user_id, item_count) VALUES (%s, %s, %s)''', (total, userId, item_len))
            mysql.connection.commit()
            cur = mysql.connection.cursor()
            cur.execute('''DELETE FROM cart WHERE user_id=%s''', [userId])
            mysql.connection.commit()
            return redirect('/cart')
        else:
            return redirect('/')
    return redirect('/')
    # return render_template('search.html')

@app.route('/admin')
def adminhome():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM customers")
    users = cur.fetchone()
    users = users[0]

    cur.execute("SELECT COUNT(*) FROM stocks")
    stocks = cur.fetchone()
    stocks = stocks[0]

    cur.execute("SELECT COUNT(*) FROM checkout")
    orders = cur.fetchone()
    orders = orders[0]

    return render_template('admin/index.html', users=users, orders=orders, stocks=stocks)

@app.route('/admin/add-new', methods=['POST','GET'])
def addnew():
    if request.method == 'POST':
        details = request.form.get
        stockname = details('stockname')
        stockdes = details('stockdes')
        stockimg = details('stockimg')
        stockprice = details('stockprice')
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO stocks (stock_name, stock_des, stock_img, stock_price) VALUES (%s, %s, %s, %s)''', (stockname, stockdes, stockimg, stockprice))
        mysql.connection.commit()
    return render_template('admin/addnew.html')

@app.route('/admin/all-stocks', methods=['POST','GET'])
def allstocks():
    cur = mysql.connection.cursor()
    cur.execute("SELECT stock_name, stock_des, stock_price, stock_id FROM stocks")
    stocks = cur.fetchall()
    return render_template('admin/allstocks.html', stocks=stocks)

@app.route('/admindelete', methods=['POST','GET'])
def admindelete():
    if request.method == 'GET':
        details = request.args.get
        stockId = details('stockId')
        cur = mysql.connection.cursor()
        cur.execute('''DELETE FROM stocks WHERE stock_id=%s''', [stockId])
        mysql.connection.commit()
        return redirect('/admin/all-stocks')
    return redirect('/')

@app.route('/admin/orders', methods=['POST','GET'])
def adminorders():
    cur = mysql.connection.cursor()
    cur.execute("SELECT b.username, b.address, b.city, b.state, a.price, a.item_count, a.check_id, a.approved FROM checkout as a JOIN customers as b ON a.user_id=b.id")
    orders = cur.fetchall()
    return render_template('admin/orders.html', orders=orders)

@app.route('/adminapprove', methods=['POST','GET'])
def adminapprove():
    if request.method == 'GET':
        details = request.args.get
        orderId = details('orderId')
        true = "true"
        cur = mysql.connection.cursor()
        cur.execute('UPDATE checkout SET approved=%s WHERE check_id=%s', (true, [orderId]))
        mysql.connection.commit()
        return redirect('/admin/orders')
    return redirect('/')

@app.route('/admin/users', methods=['POST','GET'])
def adminusers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customers ")
    users = cur.fetchall()
    print(users)
    return render_template('admin/users.html', users=users)  

if __name__==' __main__':
    app.run(debug=True)