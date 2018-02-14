from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import datetime #time stuff
import time
import re #Regex
import md5 #hasing
import os, binascii #for hasing


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
mysql = MySQLConnector(app,'mydb')
app.secret_key = '0118999881999119725'


@app.route('/')
def index():                         # run query with query_db()
    return render_template('index.html')

@app.route('/adduser')
def loadreg():
    return render_template('adduser.html')

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE email=:email"
    email = request.form['email']
    password = request.form['password']
    data = {
             'email': email
           }
    i = mysql.query_db(query, data)
    if(len(i)!=0):
        encrypted_password = md5.new(password + i[0]['salt']).hexdigest()
        if i[0]['password'] == encrypted_password:
            session['id']=i[0]['id']
            return redirect('/success')
        else:
            flash("Incorrect password")
            return redirect('/')
    else:
        flash("Email not found")
        return redirect('/')   

@app.route('/register', methods=['POST'])
def create():
  
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = request.form['password']
    

    confirm_pass=request.form['confirm_pass']

    email=request.form['email']
    birthday=request.form['birthday']

    #Validations Below
    if(len(first_name)==0):
        flash("First Name cannot be empty!")
        return redirect('/')
    elif(not first_name.isalpha()):
        flash("First Name cannot contain numbers")
        return redirect('/')
    if(len(birthday)==0):
        flash("Birthday cannot be empty!")
        return redirect('/')
    else:
        birthday = time.strptime(str(birthday), "%Y-%m-%d")
        date = datetime.date.today()
        date = time.strptime(str(date)  , "%Y-%m-%d")
        if(date < birthday):
            flash("Birthday must be in the past")
            return redirect('/')        
    if(len(last_name)==0):
        flash("Last Name cannot be empty!")
        return redirect('/')
    elif(not last_name.isalpha()):
        flash("Last Name cannot contain numbers")
        return redirect('/')

    if(len(password)==0):
        flash("Password cannot be empty!")
        return redirect('/')
    elif(len(password)<8):
        flash("Password cannot be less than 8 characters!")
        return redirect('/')
    # elif(not(any(c.isdigit() for c in password) and any(c.isupper() for c in password))):
    #     flash("Password must contain upper case letter and number")
    #     return redirect('/')

    if(len(confirm_pass)==0):
        flash("Confirm your password")
        return redirect('/')
    elif(not password == confirm_pass):
        flash("Passwords dont match")
        return redirect('/')

    if(len(email) < 1):
        flash("Email cannot be empty!")
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!") 
        return redirect('/')

        #hashing
    salt = binascii.b2a_hex(os.urandom(15))
    password = md5.new(password+salt).hexdigest()

    query = "SELECT * FROM users WHERE email=:email"
   
    #check if email exists in database already
    data = {
             'email': email
           }
    i = mysql.query_db(query, data)

    # Run query, with dictionary values injected into the query.
    query = "INSERT INTO users (first_name, last_name, email, password, salt) VALUES (:first_name, :last_name, :email, :password, :salt)" 
    if len(i)<1:
        data =  {
                    'first_name': first_name,
                    'last_name': last_name,
                    'password' : password,
                    'email': email,
                    'salt': salt
                }
        mysql.query_db(query, data)
        flash("Please login")

    else:
        flash("Email already exists")
    return redirect('/')


@app.route('/success')
def success():
    query = "SELECT * FROM users"
    result = mysql.query_db(query)                           # run query with query_db()
    return render_template('success.html', id=session['id'], users=result, debug=True)

app.run(debug=True)
