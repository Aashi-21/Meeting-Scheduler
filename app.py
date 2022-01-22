from flask import Flask, render_template, request,jsonify, redirect, url_for, session,current_app,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from PIL import Image
import stepic
import bcrypt
import shutil
from datetime import timedelta
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = 'your secret key'


# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'pythonlogin'
#app = Flask(__name__)
app.config.from_object('config.Config')
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password=%s', (username,password))
        account = cursor.fetchone()
        print(account)
        if (account):
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)




@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


@app.route('/home')
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM events ORDER BY id")
        calendar = cursor.fetchall()
        return render_template('home.html',calendar=calendar)
    return redirect(url_for('login'))


@app.route("/insert",methods=["POST","GET"])
def insert():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']
        descr = request.form['descr']
        print(title)     
        print(start)  
        cur.execute("INSERT INTO events (title,descr,start_event,end_event) VALUES (%s,%s,%s,%s)",[title,descr,start,end])
        mysql.connection.commit()
        cur.close()
        msg = 'success' 
    return jsonify(msg)

@app.route("/update",methods=["POST","GET"])
def update():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        title = request.form['title']
        start = request.form['start']
        end = request.form['end']
        descr = request.form['descr']
        id = request.form['id']
        print(title)     
        print(start)  
        cur.execute("UPDATE events SET title = %s, start_event = %s, end_event = %s, descr = %s WHERE id = %s ", [title, start, end,descr, id])
        mysql.connection.commit()      
        cur.close()
        msg = 'success' 
    return jsonify(msg)   


@app.route("/delete",methods=["POST","GET"])
def ajax_delete():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        getid = request.form['id']
        print(getid)
        cur.execute('DELETE FROM events WHERE id = {0}'.format(getid))
        mysql.connection.commit()   
        cur.close()
        msg = 'Record deleted successfully' 
    return jsonify(msg) 
  



app.run()
